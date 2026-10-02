#!/usr/bin/env bash
# Run ON THE VPS as root, after push.sh has copied the code to /srv/satbank.
# Safe to run again: it installs what's missing, refreshes the packages and restarts the app.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run as root" >&2; exit 1; }

apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip rsync debian-keyring debian-archive-keyring apt-transport-https curl gpg

# Caddy (HTTPS in front of the app), only if it isn't there yet
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -qq && apt-get install -y -qq caddy
fi

id freshbot >/dev/null 2>&1 || useradd --system --create-home --shell /usr/sbin/nologin freshbot
mkdir -p /etc/freshbot /var/lib/freshbot/satbank
chown -R freshbot:freshbot /var/lib/freshbot /srv/satbank

# one virtualenv inside the checkout (git-ignored)
[[ -d /srv/satbank/.venv ]] || sudo -H -u freshbot python3 -m venv /srv/satbank/.venv
sudo -H -u freshbot /srv/satbank/.venv/bin/pip install -q --upgrade pip
sudo -H -u freshbot /srv/satbank/.venv/bin/pip install -q -r /srv/satbank/deploy/requirements.txt

# the settings file is made once and never overwritten
if [[ ! -f /etc/freshbot/satbank.env ]]; then
  cp /srv/satbank/deploy/satbank.env.example /etc/freshbot/satbank.env
  sed -i "s/^SATF_ADMIN_TOKEN=.*/SATF_ADMIN_TOKEN=$(openssl rand -hex 24)/" /etc/freshbot/satbank.env
  chmod 600 /etc/freshbot/satbank.env
  echo "!! Edit /etc/freshbot/satbank.env (set SATF_BASE_URL), then run this script again."
fi

cp /srv/satbank/deploy/fa-satbank.service /etc/systemd/system/fa-satbank.service
systemctl daemon-reload
systemctl enable fa-satbank >/dev/null
systemctl restart fa-satbank
# the first start takes about 15 seconds (it builds its question catalogue)
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3020/ || true)
  [[ "$code" == "200" ]] && break
  sleep 2
done
echo "app answers: HTTP ${code:-none}"
systemctl --no-pager --lines=5 status fa-satbank || true
