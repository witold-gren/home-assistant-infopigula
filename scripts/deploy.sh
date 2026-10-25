#!/usr/bin/env bash
# Copy the integration into a Home Assistant configuration directory
# (by default a Samba share mounted at /Volumes/config). Restart HA afterwards.
#
#   scripts/deploy.sh                 # to /Volumes/config
#   HA_CONFIG=/other/path scripts/deploy.sh
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
target="${HA_CONFIG:-/Volumes/config}/custom_components/infopigula"

if [ ! -d "$(dirname "$target")" ]; then
  echo "Directory $(dirname "$target") not found - is the config share mounted?" >&2
  exit 1
fi

version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' \
  "$repo/custom_components/infopigula/manifest.json")"

# --inplace: no temporary files. The temporary name of __init__.py starts with
# "._", which a macOS SMB share rejects (AppleDouble).
rsync -rt --inplace --delete --exclude '__pycache__' --exclude '*.pyc' \
  "$repo/custom_components/infopigula/" "$target/"

echo "Deployed Infopiguła $version to $target"
echo "Restart Home Assistant (Settings -> System -> Restart)."
