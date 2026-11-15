#!/usr/bin/env bash
# PR 6.1: deploy static site to devops-vm with rsync, then check nginx.
# Run from WSL:  bash deploy.sh
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/pr61-site/"   # local site
HOST="devops"                                       # ssh alias -> 127.0.0.1:2222 (NAT -> guest :22)
DEST="/var/www/static-site/"                        # nginx root on server
SITE="static.devops.local"
SSH="${SSH:-/mnt/c/Windows/System32/OpenSSH/ssh.exe}"   # Windows OpenSSH (VBox NAT port is on Windows loopback)
CURL="${CURL:-/mnt/c/Windows/System32/curl.exe}"

echo "==> rsync $SRC -> $HOST:$DEST"
rsync -av --delete --chmod=D755,F644 -e "$SSH" "$SRC" "$HOST:$DEST"

echo "==> nginx -t && reload"
"$SSH" "$HOST" 'sudo nginx -t && sudo systemctl reload nginx && echo reloaded'
sleep 1   # let new nginx workers start

echo "==> check http://$SITE/ (via 127.0.0.1:80)"
PAGE=$("$CURL" -s -w '\n%{http_code}' -H "Host: $SITE" http://127.0.0.1/)
CODE=${PAGE##*$'\n'}
echo "HTTP $CODE"
grep -o '<p class="ver">[^<]*</p>' <<<"$PAGE"
[ "$CODE" = 200 ]
echo "==> done"