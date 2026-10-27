#!/usr/bin/env bash
set -euo pipefail
mkdir -p .cache
FILE="$PWD/.cache/original.apk"
SHA=11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f
URL=https://github.com/skynet909084-boop/BLOODSKY-Android/releases/download/kascada-analysis-1/KaScada.Smart.Craft.1.0.7.08.02.2026.apk
if [ ! -f "$FILE" ]; then curl -fLSs --retry 3 "$URL" -o "$FILE"; fi
echo "$SHA  $FILE" | sha256sum --check
