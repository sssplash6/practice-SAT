"""One whiteboard explainer for one bank question: AI script -> checked -> voice per step -> board.html recorded to MP4.

Usage: python3 make.py <template> <seed> <name> [--voice brian] [--model anthropic/claude-sonnet-5.5] [--no-render]
Key: OPENROUTER_API_KEY in ~/.config/satbank-openrouter.env. Output: out/<name>/ (script.json, data.js, voice.mp3, video.mp4).
"""
import argparse, json, os, pathlib, re, subprocess, sys, wave

import numpy as np
import requests

HERE = pathlib.Path(__file__).resolve().parent
CHROME = str(pathlib.Path("~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell").expanduser())
REPO = pathlib.Path("/Users/workingmyassof/freshbot/satbank")
API = "https://openrouter.ai/api/v1"
GAP, LEAD, TAIL, FPS, RATE = 0.35, 0.8, 1.8, 25, 44100

PROMPT = """You script a short whiteboard explainer video for one SAT question. The printed question sits on the
left of a whiteboard; a hand with a marker annotates it and writes notes or working on the right while a voice
narrates. You get the question with its verified answer, its explanation and why each wrong choice is wrong.

Teach HOW to get the answer, the way a great tutor would at a whiteboard.

Accuracy
- Use only what the question, the explanation and the wrong-choice reasons say. Never change the answer or add facts.
- Math: every line you write must be correct algebra and arithmetic. Check each line.

Narration ("say")
- 140 to 230 words in all. Warm, direct, short spoken sentences, second person.
- Write math for the ear: "13 x plus 7 y equals 353", never symbols.

Shape
- Reading and Writing: (1) what the question asks: mark the blank or the key words of the question; (2) find the
  evidence: highlight 2 to 4 short phrases in the passage, write one short margin note with the big idea;
  (3) predict the answer in your own words (write it); (4) eliminate each wrong choice: cross it with a 2 to 5 word
  reason; (5) tick the right choice and say in one sentence why it fits.
- Math: (1) what is asked: underline it; (2) mark the givens; (3) set up: write the equations; (4) solve one line at
  a time; (5) box the final value; (6) tick the matching choice and cross the traps with short reasons.

Steps
- 9 to 15 steps. Each step is one or two sentences of "say" plus 0 to 2 ops that show exactly what the sentence says.

Ops (JSON objects)
  {"op": "highlight", "quote": "..."}     yellow highlighter over text in the question
  {"op": "underline", "quote": "..."}
  {"op": "circle", "quote": "..."}        a word, a number or the blank
  {"op": "write", "text": "...", "box": false}   one line on the right side; "box": true boxes the final answer
  {"op": "cross", "option": "A", "note": "..."}  strike a wrong choice, note = 2 to 5 word reason
  {"op": "tick", "option": "B"}
- "quote" is copied character for character from the passage, the question or one choice, 1 to 8 words, and should
  appear only once in the question.
- "write" text is at most 26 characters; at most 9 writes in all. Plain characters only: letters, digits, spaces and
  + − × = ( ) / . , : ? Never arrows.
- Every choice gets exactly one cross or one tick. Tick the correct choice once.

Reply with JSON only: {"steps": [{"say": "...", "ops": [...]}]}"""


def key() -> str:
    for line in pathlib.Path("~/.config/satbank-openrouter.env").expanduser().read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("no OPENROUTER_API_KEY")


def post(path: str, body: dict, timeout=240) -> requests.Response:
    r = requests.post(API + path, json=body, timeout=timeout, headers={"Authorization": "Bearer " + key()})
    if r.status_code != 200:
        sys.exit(f"{path} {r.status_code}: {r.text[:400]}")
    return r


def spent() -> float:
    return requests.get(API + "/key", headers={"Authorization": "Bearer " + key()}, timeout=30).json()["data"]["usage"]


def question(template: str, seed: int) -> dict:
    sys.path.insert(0, str(REPO))
    from server import practice
    it = practice.generate(template, seed)
    topic = practice.topic_of(template)
    return {"subject": "rw" if topic.startswith("rw_") else "math", "topic_name": practice.catalogue()["topics"][topic].name,
            "text": it.text, "stem": it.stem, "choices": list(it.choices), "answer": it.answer,
            "explanation": it.rationale, "wrong_choice_reasons": {"ABCD"[i]: r for i, r in enumerate(it.reasons) if r}}


N = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "−": "-"})


def problems(script: dict, q: dict) -> list[str]:
    """What is wrong with a script, checked before any voice is paid for."""
    out, marks, writes = [], {}, []
    hay = [(q["text"] or "").translate(N), q["stem"].translate(N)] + [c.translate(N) for c in q["choices"]]
    steps = script.get("steps") or []
    if not 6 <= len(steps) <= 18:
        out.append(f"{len(steps)} steps; write 9 to 15")
    words = sum(len(s.get("say", "").split()) for s in steps)
    if not 110 <= words <= 260:
        out.append(f"narration is {words} words; keep it 140 to 230")
    for i, s in enumerate(steps, 1):
        if not s.get("say", "").strip():
            out.append(f"step {i} has no say")
        for o in s.get("ops", []):
            k = o.get("op")
            if k in ("highlight", "underline", "circle"):
                quote = (o.get("quote") or "").translate(N)
                n = sum(h.count(quote) for h in hay) if quote else 0
                if n == 0:
                    out.append(f"step {i}: quote {o.get('quote')!r} is not in the question word for word")
            elif k == "write":
                writes.append(o)
                if len(o.get("text", "")) > 30:
                    out.append(f"step {i}: write {o.get('text')!r} is over 26 characters")
                if "→" in o.get("text", ""):
                    out.append(f"step {i}: no arrows in writes")
            elif k in ("cross", "tick"):
                if o.get("option") not in ("A", "B", "C", "D")[:len(q["choices"])]:
                    out.append(f"step {i}: bad option {o.get('option')!r}")
                marks.setdefault(o.get("option"), []).append(k)
            else:
                out.append(f"step {i}: unknown op {k!r}")
    for letter in "ABCD"[:len(q["choices"])]:
        want = ["tick"] if letter == q["answer"] else ["cross"]
        if marks.get(letter) != want:
            out.append(f"choice {letter} should get exactly one {want[0]}, got {marks.get(letter)}")
    if len(writes) > 10:
        out.append(f"{len(writes)} writes; at most 9")
    if q["subject"] == "math":
        value = q["choices"]["ABCD".index(q["answer"])].translate(N).replace(" ", "")
        boxed = [o["text"].translate(N).replace(" ", "") for o in writes if o.get("box")]
        if not any(re.search(r"(^|[=:])" + re.escape(value) + r"$", b) for b in boxed):
            out.append(f"box the final answer: a boxed write ending in {value}")
    return out


def write_script(q: dict, model: str) -> dict:
    msgs = [{"role": "system", "content": PROMPT}, {"role": "user", "content": json.dumps(q, ensure_ascii=False, indent=1)}]
    for attempt in range(3):
        r = post("/chat/completions", {"model": model, "messages": msgs, "temperature": 0.4}).json()
        text = r["choices"][0]["message"]["content"]
        try:
            script = json.loads(re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M))
        except json.JSONDecodeError as e:
            bad = [f"reply was not valid JSON: {e}"]
        else:
            bad = problems(script, q)
            if not bad:
                return script
        print(f"  attempt {attempt + 1}: {len(bad)} problems: {bad}")
        msgs += [{"role": "assistant", "content": text},
                 {"role": "user", "content": "Fix these and reply with the whole JSON again:\n- " + "\n- ".join(bad)}]
    sys.exit("script still has problems after 3 tries")


def pcm(mp3: pathlib.Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16)


def voice(script: dict, out: pathlib.Path, model: str, voice_id: str) -> float:
    clips, t = [], LEAD
    for i, s in enumerate(script["steps"]):
        mp3 = out / f"step-{i:02d}.mp3"
        if not mp3.exists():
            mp3.write_bytes(post("/audio/speech", {"model": model, "input": s["say"], "voice": voice_id, "response_format": "mp3"}).content)
        a = pcm(mp3)
        s["start"], s["dur"] = round(t, 3), round(len(a) / RATE, 3)
        clips.append((t, a))
        t += len(a) / RATE + GAP
    total = t - GAP + TAIL
    track = np.zeros(int(total * RATE), np.int16)
    for start, a in clips:
        i = int(start * RATE)
        track[i:i + len(a)] = a
    with wave.open(str(out / "voice.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(track.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "voice.wav"), "-b:a", "128k", str(out / "voice.mp3")], check=True)
    return round(total, 3)


def render(out: pathlib.Path, total: float) -> None:
    from playwright.sync_api import sync_playwright
    url = (HERE / "board.html").as_uri() + "?capture=1&d=" + out.as_uri() + "/"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                           "-i", str(out / "voice.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                           str(out / "video.mp4")], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        page = b.new_page(viewport={"width": 1920, "height": 1080})
        page.on("console", lambda m: print("  page:", m.text) if m.type in ("warning", "error") else None); page.on("pageerror", lambda e: sys.exit(f"page error: {e}"))
        page.goto(url)
        page.wait_for_function("window.READY === true", timeout=30000)
        frames = int(total * FPS)
        for f in range(frames):
            page.evaluate("t => seek(t)", f / FPS)
            ff.stdin.write(page.screenshot(type="jpeg", quality=90))
            if f % (FPS * 10) == 0:
                print(f"  frame {f}/{frames}")
        b.close()
    ff.stdin.close()
    ff.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template"); ap.add_argument("seed", type=int); ap.add_argument("name")
    ap.add_argument("--voice", default="brian"); ap.add_argument("--tts", default="elevenlabs/eleven-v4-turbo")
    ap.add_argument("--model", default="anthropic/claude-sonnet-5.5"); ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    out = HERE / "out" / a.name
    out.mkdir(parents=True, exist_ok=True)
    before = spent()
    q = question(a.template, a.seed)
    sf = out / "script.json"
    script = json.loads(sf.read_text()) if sf.exists() else write_script(q, a.model)
    sf.write_text(json.dumps(script, ensure_ascii=False, indent=1))
    print(f"script: {len(script['steps'])} steps, {sum(len(s['say'].split()) for s in script['steps'])} words")
    total = voice(script, out, a.tts, a.voice)
    board = {"q": {k: q[k] for k in ("subject", "topic_name", "text", "stem", "choices", "answer")},
             "steps": script["steps"], "total": total, "audio": "voice.mp3"}
    (out / "data.js").write_text("window.BOARD = " + json.dumps(board, ensure_ascii=False) + ";\n")
    print(f"voice: {total:.1f} s, spent ${spent() - before:.4f} on this run")
    if not a.no_render:
        render(out, total)
        print("video:", out / "video.mp4")


if __name__ == "__main__":
    main()
