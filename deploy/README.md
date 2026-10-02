# Hosting SAT Freshman on your own VPS

One small program (FastAPI + a SQLite file) that serves the pages and the API itself.
Caddy sits in front for HTTPS. Written for Ubuntu 24.04 like the rest of the freshbot VPS kit.

## What you need
- The VPS's address and a way to log in (`ssh root@IP`, or the alias you already use).
- A domain or sub-domain (for example `sat.yourdomain.com`) with an **A record pointing at the VPS IP**.
  No domain yet? It still works over plain `http://IP` (see the end of `Caddyfile.snippet`).

## Steps (about 15 minutes)

1. **On your laptop**, from the repository root, copy the code up and install it:
   ```
   bash deploy/push.sh root@YOUR.VPS.IP
   ```
   It installs Python and Caddy, makes the `freshbot` user, builds the virtualenv, installs
   the service `fa-satbank` and starts it. The first time it tells you to edit the settings.
2. **On the VPS**, set your address:
   ```
   nano /etc/freshbot/satbank.env      # set SATF_BASE_URL=https://sat.yourdomain.com
   ```
3. **On the VPS**, add the site to Caddy: put the block from `deploy/Caddyfile.snippet` into
   `/etc/caddy/Caddyfile` (with your domain), then:
   ```
   caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
   ```
   Caddy gets the HTTPS certificate by itself once the DNS record points at the VPS.
4. Run step 1's command again (it is safe to repeat) so the app restarts with the new address,
   then open your address in a browser.

## Updating later
Run `bash deploy/push.sh root@YOUR.VPS.IP` again. It re-copies the code, refreshes packages and
restarts. The database (`/var/lib/freshbot/satbank/`) and the settings file are never overwritten.

## Look after it
```
systemctl status fa-satbank          # is it running
journalctl -u fa-satbank -f          # live log
cp /var/lib/freshbot/satbank/satfreshman.db /root/satbank-$(date +%F).db   # a quick backup
```
Start with an empty database (the default). To carry your sandbox people and data across instead,
copy `prev5.db` to `/var/lib/freshbot/satbank/satfreshman.db` while the service is stopped
(`systemctl stop fa-satbank`), fix the owner (`chown freshbot:freshbot ...`) and start it again.

## Notes
- Mail: without `SATF_SMTP_*` set, emails are written to `server/outbox` instead of being sent.
- The app keeps its question material (`material/`, about 150 MB) next to the code; `push.sh` copies it.
- Port 3020 is loopback only; only Caddy talks to the internet (open 80 and 443 in the VPS firewall).
