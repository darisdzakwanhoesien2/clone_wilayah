#!/usr/bin/env bash
# Deploy the static Wilayah Indonesia site (index.html, demo.html, api/) to the nginx webroot.
# Usage: ./deploy/deploy.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEBROOT="/var/www/wilayah"

echo "Deploying $REPO_DIR/{index.html,demo.html,api} to $WEBROOT"

sudo mkdir -p "$WEBROOT"
sudo rsync -a --delete \
  "$REPO_DIR/index.html" \
  "$REPO_DIR/demo.html" \
  "$REPO_DIR/api" \
  "$WEBROOT/"
sudo chown -R www-data:www-data "$WEBROOT"
sudo find "$WEBROOT" -type d -exec chmod 755 {} +
sudo find "$WEBROOT" -type f -exec chmod 644 {} +

sudo nginx -t
sudo systemctl reload nginx
echo "Done. https://wilayah.darisdzakwanhoesien.site/"
