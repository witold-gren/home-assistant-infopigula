#!/usr/bin/env bash
# Kopiuje integrację do konfiguracji Home Assistant (domyślnie udział Samby
# zamontowany na Macu). Po wdrożeniu trzeba zrestartować HA.
#
#   scripts/deploy.sh                 # do /Volumes/config
#   HA_CONFIG=/inna/sciezka scripts/deploy.sh
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
target="${HA_CONFIG:-/Volumes/config}/custom_components/infopigula"

if [ ! -d "$(dirname "$target")" ]; then
  echo "Brak katalogu $(dirname "$target") - czy udział config jest zamontowany?" >&2
  exit 1
fi

version="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' \
  "$repo/custom_components/infopigula/manifest.json")"

# --inplace: bez plików tymczasowych. Tymczasowa nazwa __init__.py zaczyna się
# od "._", a takich nazw udział SMB z macOS nie przyjmuje (AppleDouble).
rsync -rt --inplace --delete --exclude '__pycache__' --exclude '*.pyc' \
  "$repo/custom_components/infopigula/" "$target/"

echo "Wdrożono Infopiguła $version do $target"
echo "Zrestartuj Home Assistant (Ustawienia → System → Uruchom ponownie)."
