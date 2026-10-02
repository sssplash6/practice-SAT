#!/usr/bin/env bash
# Run ON YOUR LAPTOP from the repository root:   bash deploy/push.sh root@YOUR.VPS.IP
# Copies the code to /srv/satbank on the VPS and runs deploy/remote-setup.sh there.
# Never copies: git history, local databases, caches, worktrees.
set -euo pipefail
HOST="${1:?usage: bash deploy/push.sh user@host}"
ssh "$HOST" 'mkdir -p /srv/satbank'
rsync -az --delete \
  --exclude '.git' --exclude '.claude' --exclude '.venv' --exclude '__pycache__' \
  --exclude '*.db' --exclude '*.db-shm' --exclude '*.db-wal' \
  --exclude 'server/cache' --exclude 'server/outbox' --exclude '/.playwright-mcp' \
  --exclude '/archive' --exclude '/poc' --exclude '/spec' \
  ./ "$HOST":/srv/satbank/
ssh "$HOST" 'bash /srv/satbank/deploy/remote-setup.sh'
