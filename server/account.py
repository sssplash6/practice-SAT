"""Email identity, device credentials, and approved device transfers."""

from __future__ import annotations

import hashlib
import hmac
import base64
import json
import logging
import os
import re
import secrets
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

from . import db, deps, mail, progress

router = APIRouter()
log = logging.getLogger("satf.account")
_limits: dict[tuple[str, str], list[float]] = defaultdict(list)
_google_keys: tuple[float, list[dict]] = (0, [])


def init() -> None:
    db.run("CREATE TABLE IF NOT EXISTS passkey_users (learner TEXT PRIMARY KEY,user_handle TEXT NOT NULL)")
    db.run("CREATE TABLE IF NOT EXISTS email_changes (user_id TEXT PRIMARY KEY,learner TEXT NOT NULL,"
           "old_user TEXT NOT NULL,created TEXT NOT NULL)")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(value: str, label: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, f"invalid {label}") from exc


def _rp() -> tuple[str, str]:
    raw = os.environ.get("SATF_BASE_URL", "http://localhost:8000")
    parsed = urlsplit(raw)
    if not parsed.scheme or not parsed.hostname:
        raise RuntimeError("SATF_BASE_URL must be an absolute URL")
    return parsed.hostname, f"{parsed.scheme}://{parsed.netloc}"


def _challenge(learner: str, purpose: str) -> tuple[str, str]:
    challenge = _b64(secrets.token_bytes(32))
    ttl = max(1, min(3600, int(os.environ.get("SATF_WEBAUTHN_TTL", "300"))))
    expires = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat(timespec="seconds")
    db.run("INSERT INTO webauthn_challenges(challenge,learner,purpose,expires) VALUES (?,?,?,?)",
           challenge, learner, purpose, expires)
    return challenge, expires


def _consume_challenge(challenge: str, purpose: str, learner: str | None = None) -> None:
    with db.transaction():
        row = db.one("SELECT * FROM webauthn_challenges WHERE challenge=?", challenge)
        if not row or row["purpose"] != purpose or _expired(row["expires"]) or (
                learner is not None and row["learner"] != learner):
            raise HTTPException(400, "passkey challenge expired")
        db.run("DELETE FROM webauthn_challenges WHERE challenge=?", challenge)


def _client(body: dict, kind: str, purpose: str, learner: str | None = None) -> tuple[bytes, bytes]:
    raw = _unb64(str(body.get("clientDataJSON") or body.get("client_data_json") or ""),
                 "client data")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "invalid client data") from exc
    if data.get("type") != kind or data.get("origin") != _rp()[1]:
        raise HTTPException(400, "wrong passkey origin or operation")
    challenge = data.get("challenge")
    if not isinstance(challenge, str):
        raise HTTPException(400, "missing passkey challenge")
    _consume_challenge(challenge, purpose, learner)
    auth = _unb64(str(body.get("authData") or body.get("authenticatorData") or
                      body.get("authenticator_data") or ""), "authenticator data")
    if len(auth) < 37 or auth[:32] != hashlib.sha256(_rp()[0].encode()).digest() or not auth[32] & 1:
        raise HTTPException(400, "invalid authenticator data")
    return raw, auth


@router.post("/api/passkey/register/options")
def passkey_register_options(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    existing = db.one("SELECT user_handle FROM passkey_users WHERE learner=?", learner)
    user_handle = existing["user_handle"] if existing else _b64(secrets.token_bytes(16))
    db.run("INSERT OR IGNORE INTO passkey_users(learner,user_handle) VALUES (?,?)", learner, user_handle)
    challenge, expires = _challenge(learner, "register")
    rp_id, _ = _rp()
    row = db.one("SELECT name,handle FROM learners WHERE id=?", learner)
    name = (row["name"] or row["handle"]) if row else None
    name = name or "Student"
    return {"challenge": challenge, "expires": expires, "timeout": 300000,
            "rp": {"id": rp_id, "name": "SAT Freshman"}, "rpId": rp_id,
            "user": {"id": user_handle, "name": name, "displayName": name},
            "pubKeyCredParams": [{"type": "public-key", "alg": -7},
                                 {"type": "public-key", "alg": -257}],
            "authenticatorSelection": {"residentKey": "required", "userVerification": "preferred"}}


@router.post("/api/passkey/register")
def passkey_register(body: dict, request: Request,
                     x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    _raw, auth = _client(body, "webauthn.create", "register", learner)
    cred_id = str(body.get("id") or body.get("credential_id") or "")
    spki = _unb64(str(body.get("publicKey") or body.get("public_key") or body.get("spki") or ""),
                  "public key")
    alg = int(body.get("algorithm", body.get("alg", 0)))
    try:
        key = serialization.load_der_public_key(spki)
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, "invalid public key") from exc
    if not cred_id or not ((alg == -7 and isinstance(key, ec.EllipticCurvePublicKey) and
                            isinstance(key.curve, ec.SECP256R1)) or
                           (alg == -257 and isinstance(key, rsa.RSAPublicKey))):
        raise HTTPException(400, "unsupported passkey")
    count = int.from_bytes(auth[33:37], "big")
    try:
        db.run("INSERT INTO passkeys(cred_id,learner,user_handle,spki,alg,sign_count,label,created)"
               " VALUES (?,?,?,?,?,?,?,?)", cred_id, learner,
               db.one("SELECT user_handle FROM passkey_users WHERE learner=?", learner)["user_handle"],
               spki, alg, count, str(body.get("label") or "Passkey")[:80], deps.now())
    except Exception as exc:
        if db.one("SELECT 1 FROM passkeys WHERE cred_id=?", cred_id):
            raise HTTPException(409, "passkey already registered") from exc
        raise
    start_swap(learner)
    return _credential(learner, learner, carry=False, session_only=False,
                       method="passkey", request=request)


class PasskeyOptions(BaseModel):
    conditional: bool = False


@router.post("/api/passkey/login/options")
def passkey_login_options(body: PasskeyOptions) -> dict:
    challenge, expires = _challenge("", "login")
    rp_id, _ = _rp()
    return {"challenge": challenge, "rpId": rp_id, "timeout": 300000,
            "expires": expires, "allowCredentials": [], "userVerification": "preferred"}


@router.post("/api/passkey/login")
def passkey_login(body: dict, request: Request,
                  x_learner: str | None = Header(default=None)) -> dict:
    source = deps.writer_of(x_learner)
    raw, auth = _client(body, "webauthn.get", "login")
    cred_id = str(body.get("id") or body.get("credential_id") or "")
    row = db.one("SELECT * FROM passkeys WHERE cred_id=?", cred_id)
    if not row:
        raise HTTPException(401, "unknown passkey")
    sig = _unb64(str(body.get("signature") or ""), "signature")
    signed = auth + hashlib.sha256(raw).digest()
    key = serialization.load_der_public_key(row["spki"])
    try:
        if row["alg"] == -7:
            key.verify(sig, signed, ec.ECDSA(hashes.SHA256()))
        elif row["alg"] == -257:
            key.verify(sig, signed, padding.PKCS1v15(), hashes.SHA256())
        else:
            raise HTTPException(401, "unsupported passkey")
    except InvalidSignature as exc:
        raise HTTPException(401, "invalid passkey signature") from exc
    count = int.from_bytes(auth[33:37], "big")
    if count and count <= int(row["sign_count"] or 0):
        log.warning("passkey sign counter did not increase for %s", cred_id[:8])
    db.run("UPDATE passkeys SET sign_count=?,last_used=? WHERE cred_id=?",
           max(count, int(row["sign_count"] or 0)), deps.now(), cred_id)
    return _credential(row["learner"], source, carry=bool(body.get("carry", False)),
                       session_only=bool(body.get("session_only", False)), method="passkey", request=request)


@router.get("/api/passkeys")
def passkeys(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.learner_of(x_learner)
    return {"items": [{k: r[k] for k in ("cred_id", "label", "created", "last_used")}
                      for r in db.rows("SELECT cred_id,label,created,last_used FROM passkeys"
                                       " WHERE learner=? ORDER BY created", learner)]}


@router.delete("/api/passkeys/{cred_id}")
def remove_passkey(cred_id: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    if not db.run("DELETE FROM passkeys WHERE cred_id=? AND learner=?", cred_id, learner).rowcount:
        raise HTTPException(404, "no such passkey")
    return {"ok": True}


def _google_enabled() -> str:
    client_id = os.environ.get("SATF_GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(404, "Google sign-in is not configured")
    return client_id


def _jwks(force: bool = False) -> list[dict]:
    global _google_keys
    if not force and _google_keys[0] > time.monotonic():
        return _google_keys[1]
    req = urllib.request.Request(os.environ.get("SATF_GOOGLE_JWKS_URL",
                                        "https://www.googleapis.com/oauth2/v3/certs"))
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.load(response)
            cache = response.headers.get("Cache-Control", "")
    except (OSError, ValueError) as exc:
        raise HTTPException(503, "Google keys are unavailable") from exc
    seconds = int((re.search(r"max-age=(\d+)", cache) or [None, "300"])[1])
    keys = data.get("keys")
    if not isinstance(keys, list):
        raise HTTPException(503, "Google keys are unavailable")
    _google_keys = (time.monotonic() + min(seconds, 86400), keys)
    return keys


@router.post("/api/google/nonce")
def google_nonce(x_learner: str | None = Header(default=None)) -> dict:
    _google_enabled()
    learner = deps.writer_of(x_learner)
    nonce = _b64(secrets.token_bytes(24))
    expires = _expires(5)
    db.run("INSERT INTO webauthn_challenges(challenge,learner,purpose,expires) VALUES (?,?,?,?)",
           nonce, learner, "google", expires)
    return {"nonce": nonce, "expires": expires}


class GoogleLogin(BaseModel):
    credential: str = Field(max_length=10000)
    nonce: str = Field(max_length=200)
    carry: bool = False
    session_only: bool = False


@router.post("/api/google")
def google_login(body: GoogleLogin, request: Request,
                 x_learner: str | None = Header(default=None)) -> dict:
    client_id = _google_enabled()
    source = deps.writer_of(x_learner)
    parts = body.credential.split(".")
    if len(parts) != 3:
        raise HTTPException(401, "invalid Google token")
    try:
        header = json.loads(_unb64(parts[0], "Google header"))
        claims = json.loads(_unb64(parts[1], "Google claims"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(401, "invalid Google token") from exc
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise HTTPException(401, "invalid Google token")
    if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
        raise HTTPException(401, "invalid Google signature algorithm")
    key = next((k for k in _jwks() if k.get("kid") == header["kid"]), None)
    if key is None:
        key = next((k for k in _jwks(force=True) if k.get("kid") == header["kid"]), None)
    if not key or key.get("kty") != "RSA":
        raise HTTPException(401, "unknown Google signing key")
    try:
        public = rsa.RSAPublicNumbers(int.from_bytes(_unb64(key["e"], "exponent"), "big"),
                                      int.from_bytes(_unb64(key["n"], "modulus"), "big")).public_key()
        public.verify(_unb64(parts[2], "signature"), f"{parts[0]}.{parts[1]}".encode(),
                      padding.PKCS1v15(), hashes.SHA256())
    except (InvalidSignature, ValueError, KeyError) as exc:
        raise HTTPException(401, "invalid Google signature") from exc
    expiry = claims.get("exp")
    if not isinstance(expiry, (int, float)) or isinstance(expiry, bool):
        raise HTTPException(401, "invalid Google claims")
    if (claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com") or
            claims.get("aud") != client_id or expiry < time.time() - 60 or
            claims.get("email_verified") is not True or claims.get("nonce") != body.nonce or
            not claims.get("sub") or not claims.get("email")):
        raise HTTPException(401, "invalid Google claims")
    _consume_challenge(body.nonce, "google", source)
    email = str(claims["email"]).lower()
    row = db.one("SELECT * FROM users WHERE google_sub=?", str(claims["sub"]))
    if row is None:
        row = db.one("SELECT * FROM users WHERE email=?", email)
    target = row["learner"] if row and row["learner"] else source
    with db.transaction():
        if row:
            if row["google_sub"] and row["google_sub"] != claims["sub"]:
                raise HTTPException(409, "email is linked to another Google account")
            db.run("UPDATE users SET google_sub=?,verified=1,learner=?,last_login=? WHERE id=?",
                   str(claims["sub"]), target, deps.now(), row["id"])
        else:
            db.run("INSERT INTO users(id,first,last,email,verified,created,learner,google_sub,last_login)"
                   " VALUES (?,?,?,?,1,?,?,?,?)", secrets.token_urlsafe(12),
                   str(claims.get("given_name") or email.split("@")[0])[:60],
                   str(claims.get("family_name") or "")[:60], email, deps.now(), target,
                   str(claims["sub"]), deps.now())
    if not row or row["learner"] is None:
        start_swap(target)
    return _credential(target, source, carry=body.carry, session_only=body.session_only,
                       method="google", request=request)


def _expires(minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat(timespec="seconds")


def _expired(value: str | None) -> bool:
    return not value or datetime.fromisoformat(value) <= datetime.now(timezone.utc)


def _mask(email: str) -> str:
    local, domain = email.split("@", 1)
    return local[:1] + "•••@" + domain


def _limit(kind: str, key: str, n: int, seconds: int) -> None:
    now = time.monotonic()
    bucket = _limits[(kind, key)]
    bucket[:] = [x for x in bucket if now - x < seconds]
    if len(bucket) >= n:
        raise HTTPException(429, "try again later")
    bucket.append(now)


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def saved(learner: str) -> bool:
    """One definition of a saved account for all sections."""
    if db.one("SELECT 1 FROM passkeys WHERE learner=? LIMIT 1", learner):
        return True
    return bool(db.one("SELECT 1 FROM users WHERE learner=? AND (verified=1 OR google_sub IS NOT NULL)"
                       " LIMIT 1", learner))


def start_swap(learner: str) -> None:
    """Allow old anonymous-code browsers to acquire device keys for 14 days."""
    if learner.startswith("a:"):
        db.ensure_learner(learner)
        db.run("UPDATE learners SET swap_until=? WHERE id=?", _expires(14 * 24 * 60), learner)


def _credential(target: str, source: str, *, carry: bool, session_only: bool,
                method: str, request: Request) -> dict:
    moved = progress.carry(source, target) if carry and source != target and not session_only else 0
    token = deps.mint_device(target, method, deps._label(request.headers.get("user-agent", "")), session_only,
                             _expires(12 * 60) if session_only else None)
    out = {"credential": token, "saved": saved(target), "moved": moved}
    if (request.headers.get("x-learner") or "").startswith("a:"):
        out["learner"] = target
    return out


class LinkEmail(BaseModel):
    email: EmailStr


@router.post("/api/account/link")
def link_email(body: LinkEmail, request: Request, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    email = str(body.email).strip().lower()
    _limit("email", email, 1, 60)
    _limit("email-learner", learner, 5, 3600)
    _limit("email-ip", _ip(request), 5, 3600)
    token = secrets.token_urlsafe(24)
    code = f"{secrets.randbelow(1_000_000):06d}"
    digest = hashlib.sha256(code.encode()).hexdigest()
    with db.transaction():
        row = db.one("SELECT id FROM users WHERE email=?", email)
        if row is None:
            uid = secrets.token_urlsafe(12)
            db.run("INSERT INTO users(id,first,last,email,created) VALUES (?,?,?,?,?)",
                   uid, "", "", email, deps.now())
        else:
            uid = row["id"]
        db.run("UPDATE users SET login_token=?,login_code=?,login_for=?,login_sent=?,login_tries=0"
               " WHERE id=?", token, digest, learner, deps.now(), uid)
    delivery = mail.send_login(email, code, token)
    return {"sent": True, "delivery": delivery, "email_masked": _mask(email)}


@router.put("/api/account/email")
def change_email(body: LinkEmail, request: Request,
                 x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    old = db.one("SELECT id,email FROM users WHERE learner=? AND verified=1 ORDER BY created LIMIT 1", learner)
    if not old:
        raise HTTPException(409, "save an email account first")
    email = str(body.email).strip().lower()
    if email == old["email"]:
        return {"sent": False, "email_masked": _mask(email)}
    other = db.one("SELECT id,learner FROM users WHERE email=?", email)
    if other and other["learner"]:
        raise HTTPException(409, "that email is linked to another learner")
    _limit("email", email, 1, 60)
    _limit("email-learner", learner, 5, 3600)
    _limit("email-ip", _ip(request), 5, 3600)
    token = secrets.token_urlsafe(24)
    code = f"{secrets.randbelow(1_000_000):06d}"
    with db.transaction():
        uid = other["id"] if other else secrets.token_urlsafe(12)
        if not other:
            db.run("INSERT INTO users(id,first,last,email,created) VALUES (?,?,?,?,?)",
                   uid, "", "", email, deps.now())
        db.run("UPDATE users SET login_token=?,login_code=?,login_for=?,login_sent=?,login_tries=0"
               " WHERE id=?", token, hashlib.sha256(code.encode()).hexdigest(), learner, deps.now(), uid)
        db.run("DELETE FROM email_changes WHERE learner=?", learner)
        db.run("INSERT INTO email_changes(user_id,learner,old_user,created) VALUES (?,?,?,?)",
               uid, learner, old["id"], deps.now())
    delivery = mail.send_login(email, code, token)
    return {"sent": True, "delivery": delivery, "email_masked": _mask(email)}


class VerifyEmail(BaseModel):
    code: str | None = None
    token: str | None = None
    here: bool = False
    carry: bool = False
    session_only: bool = False


@router.post("/api/account/verify")
def verify_email(body: VerifyEmail, request: Request,
                 x_learner: str | None = Header(default=None)) -> dict:
    source = deps.writer_of(x_learner)
    if bool(body.code) == bool(body.token):
        raise HTTPException(422, "send a code or token")
    if body.token:
        row = db.one("SELECT * FROM users WHERE login_token=?", body.token)
        if row is None:
            raise HTTPException(410, "that link has expired")
        if row["login_for"] != source and not body.here:
            if _expired(row["login_sent"] and (datetime.fromisoformat(row["login_sent"]) +
                                                   timedelta(minutes=30)).isoformat()):
                raise HTTPException(410, "that link has expired")
            # Possession of the mailed link proves the mailbox; the requesting
            # browser still has to enter the shown code to finish its own login.
            code = f"{secrets.randbelow(1_000_000):06d}"
            db.run("UPDATE users SET login_code=? WHERE id=?",
                   hashlib.sha256(code.encode()).hexdigest(), row["id"])
            return {"other_device": True, "code": code}
    else:
        if not body.code or not body.code.isdigit() or len(body.code) != 6:
            raise HTTPException(422, "enter the six-digit code")
        row = db.one("SELECT * FROM users WHERE login_for=? AND login_sent IS NOT NULL"
                     " ORDER BY login_sent DESC LIMIT 1", source)
        if row is None:
            raise HTTPException(410, "no code is pending")
        digest = hashlib.sha256(body.code.encode()).hexdigest()
        if not hmac.compare_digest(row["login_code"] or "", digest):
            tries = int(row["login_tries"] or 0) + 1
            db.run("UPDATE users SET login_tries=? WHERE id=?", tries, row["id"])
            if tries >= 5:
                db.run("UPDATE users SET login_token=NULL,login_code=NULL,login_sent=NULL"
                       " WHERE id=?", row["id"])
                raise HTTPException(410, "too many wrong codes")
            raise HTTPException(400, "wrong code")
    expiry = (datetime.fromisoformat(row["login_sent"]) + timedelta(minutes=30)).isoformat() \
        if row["login_sent"] else None
    if _expired(expiry) or int(row["login_tries"] or 0) >= 5:
        raise HTTPException(410, "that code has expired")
    change = db.one("SELECT * FROM email_changes WHERE user_id=?", row["id"])
    target = change["learner"] if change else row["learner"] or source
    with db.transaction():
        db.run("UPDATE users SET verified=1, learner=?, last_login=?,login_token=NULL,"
               "login_code=NULL,login_for=NULL,login_sent=NULL,login_tries=0 WHERE id=?",
               target, deps.now(), row["id"])
        if change:
            db.run("UPDATE users SET learner=NULL WHERE id=? AND learner=?", change["old_user"], target)
            db.run("DELETE FROM email_changes WHERE user_id=?", row["id"])
    if row["learner"] is None:
        start_swap(target)
    return _credential(target, source, carry=body.carry, session_only=body.session_only,
                       method="email", request=request)


@router.get("/api/account")
def get_account(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.learner_of(x_learner)
    row = db.one("SELECT email,verified,created,login_sent FROM users WHERE learner=?"
                 " ORDER BY verified DESC,created LIMIT 1", learner)
    return {"saved": saved(learner), "email": row["email"] if row else None,
            "email_masked": _mask(row["email"]) if row and row["email"] else None,
            "verified": bool(row and row["verified"]), "since": row["created"] if row else None,
            "pending": bool(db.one("SELECT 1 FROM users WHERE login_for=? AND login_sent IS NOT NULL", learner))}


@router.delete("/api/account")
def unlink_account(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    db.run("UPDATE users SET learner=NULL WHERE learner=?", learner)
    return {"ok": True}


class LinkRequest(BaseModel):
    device: str = Field(default="Browser", max_length=40)
    session_only: bool = False


@router.post("/api/link/request")
def request_link(body: LinkRequest, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    token = secrets.token_urlsafe(24)
    code = f"{secrets.randbelow(1_000_000):06d}"
    expiry = _expires(10)
    for _ in range(10):
        if not db.one("SELECT 1 FROM pairs WHERE code=?", code):
            break
        code = f"{secrets.randbelow(1_000_000):06d}"
    else:
        raise HTTPException(503, "could not make a device code")
    db.run("INSERT INTO pairs(code,learner,created,expires,state,dir,token,req_device,session_only)"
           " VALUES (?,?,?,?,?,?,?,?,?)", code, learner, deps.now(), expiry, "open", "pull",
           token, body.device.strip() or "Browser", int(body.session_only))
    return {"token": token, "code": code, "expires": expiry}


class LinkCode(BaseModel):
    code: str = Field(min_length=6, max_length=6)


@router.post("/api/link/code")
def inspect_link(body: LinkCode, request: Request,
                 x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.learner_of(x_learner)
    _limit("link-ip", _ip(request), 10, 600)
    row = db.one("SELECT * FROM pairs WHERE code=? AND dir='pull'", body.code)
    if not row:
        raise HTTPException(404, "no such device code")
    if _expired(row["expires"]) or row["state"] in ("used", "denied"):
        raise HTTPException(410, "device code expired")
    if row["learner"] == learner:
        raise HTTPException(409, "use another device")
    return {"token": row["token"], "device": row["req_device"],
            "session_only": bool(row["session_only"]), "state": row["state"]}


@router.get("/api/link/{token}")
def link_status(token: str, request: Request, carry: bool = False,
                x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    row = db.one("SELECT * FROM pairs WHERE token=? AND dir='pull'", token)
    if not row or row["learner"] != learner:
        raise HTTPException(404, "no such request")
    if _expired(row["expires"]) or row["state"] == "used":
        raise HTTPException(410, "device code expired")
    if row["state"] == "denied":
        return {"state": "denied"}
    if row["state"] != "allowed":
        return {"state": "pending"}
    with db.transaction():
        if not db.run("UPDATE pairs SET state='used',used=? WHERE token=? AND state='allowed'",
                      deps.now(), token).rowcount:
            raise HTTPException(410, "device code used")
    result = _credential(row["approver"], learner, carry=carry,
                         session_only=bool(row["session_only"]), method="phone", request=request)
    return {"state": "allowed", **result}


@router.post("/api/link/{token}/approve")
def approve_link(token: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    row = db.one("SELECT * FROM pairs WHERE token=? AND dir='pull'", token)
    if not row:
        raise HTTPException(404, "no such request")
    if _expired(row["expires"]) or row["state"] != "open":
        raise HTTPException(410, "device code expired")
    if row["learner"] == learner:
        raise HTTPException(409, "use another device")
    db.run("UPDATE pairs SET state='allowed',approver=? WHERE token=?", learner, token)
    return {"ok": True}


@router.post("/api/link/{token}/deny")
def deny_link(token: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    row = db.one("SELECT * FROM pairs WHERE token=? AND dir='pull'", token)
    if not row:
        raise HTTPException(404, "no such request")
    if _expired(row["expires"]) or row["state"] != "open":
        raise HTTPException(410, "device code expired")
    if row["learner"] == learner:
        raise HTTPException(409, "use another device")
    db.run("UPDATE pairs SET state='denied' WHERE token=?", token)
    return {"ok": True}


@router.post("/api/transfer")
def transfer_code(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    code = db.new_code(8)
    expiry = _expires(10)
    db.run("INSERT INTO transfers(code,learner,expires) VALUES (?,?,?)", code, learner, expiry)
    return {"code": code, "expires": expiry}


class Redeem(BaseModel):
    code: str
    carry: bool = False
    session_only: bool = False


@router.post("/api/transfer/redeem")
def redeem_transfer(body: Redeem, request: Request,
                    x_learner: str | None = Header(default=None)) -> dict:
    source = deps.writer_of(x_learner)
    _limit("transfer-ip", _ip(request), 10, 600)
    with db.transaction():
        row = db.one("SELECT * FROM transfers WHERE code=?", body.code.upper().replace(" ", ""))
        if not row:
            raise HTTPException(404, "no such transfer code")
        if row["used"] or _expired(row["expires"]):
            raise HTTPException(410, "transfer code expired")
        db.run("UPDATE transfers SET used=? WHERE code=?", deps.now(), row["code"])
    target = row["learner"]
    if not saved(target):
        return {"credential": target, "saved": False, "moved": 0}
    return _credential(target, source, carry=body.carry, session_only=body.session_only,
                       method="transfer", request=request)


def _device_id(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:20]


@router.get("/api/devices")
def devices(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.learner_of(x_learner)
    rows = db.rows("SELECT token,label,method,created,last_seen,session_only,expires,revoked"
                   " FROM devices WHERE learner=? ORDER BY created DESC", learner)
    return {"items": [{"id": _device_id(r["token"]), "label": r["label"], "method": r["method"],
                       "created": r["created"], "last_seen": r["last_seen"],
                       "session_only": bool(r["session_only"]), "expires": r["expires"],
                       "revoked": r["revoked"], "this": r["token"] == x_learner}
                      for r in rows], "old_code_until": (db.one("SELECT swap_until FROM learners WHERE id=?",
                                                                  learner) or {"swap_until": None})["swap_until"]}


def _own_device(token: str | None) -> str:
    deps.learner_of(token)
    if not token or not token.startswith("d:"):
        raise HTTPException(400, "use a device credential")
    return token


@router.post("/api/devices/this/ping")
def ping_device(x_learner: str | None = Header(default=None)) -> dict:
    token = _own_device(x_learner)
    db.run("UPDATE devices SET last_seen=?,expires=NULL WHERE token=? AND session_only=1",
           deps.now(), token)
    return {"ok": True}


@router.post("/api/devices/this/leaving")
def leave_device(x_learner: str | None = Header(default=None)) -> dict:
    token = _own_device(x_learner)
    db.run("UPDATE devices SET expires=? WHERE token=? AND session_only=1", _expires(1), token)
    return {"ok": True}


@router.delete("/api/devices/this")
def revoke_this(x_learner: str | None = Header(default=None)) -> dict:
    token = _own_device(x_learner)
    db.run("UPDATE devices SET revoked=? WHERE token=?", deps.now(), token)
    return {"ok": True}


@router.delete("/api/devices/{device_id}")
def revoke_device(device_id: str, x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    row = next((r for r in db.rows("SELECT token FROM devices WHERE learner=? AND revoked IS NULL", learner)
                if hmac.compare_digest(_device_id(r["token"]), device_id)), None)
    if not row:
        raise HTTPException(404, "no such device")
    db.run("UPDATE devices SET revoked=? WHERE token=?", deps.now(), row["token"])
    return {"ok": True}


@router.post("/api/devices/signout-others")
def signout_others(x_learner: str | None = Header(default=None)) -> dict:
    learner = deps.writer_of(x_learner)
    db.run("UPDATE devices SET revoked=? WHERE learner=? AND token<>? AND revoked IS NULL",
           deps.now(), learner, x_learner)
    db.run("UPDATE learners SET swap_until=? WHERE id=?", deps.now(), learner)
    return {"ok": True}


def shell_part(learner: str, tz: int = 0) -> dict:
    """The account-owned inbox and weekly goal pips in the shared shell."""
    from .api_profile import feed, week_goals
    inbox = feed(learner, limit=3, unread=True)
    return {"inbox": inbox, "goals": [{k: g[k] for k in ("title", "have", "target", "done")}
                                       for g in week_goals(learner, tz=tz)]}
