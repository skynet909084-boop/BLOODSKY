#!/usr/bin/env bash
# Download exact hash-pinned authorized input from the *archived private* legacy repo.
# Never publish the original APK, or put GitHub credentials into this public repository.
set -euo pipefail
mkdir -p .cache
FILE="$PWD/.cache/original.apk"
SHA="11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f"
SOURCE_REPO="skynet909084-boop/BLOODSKY-Android"
TAG="kascada-analysis-1"
ASSET="KaScada.Smart.Craft.1.0.7.08.02.2026.apk"
if [ -f "$FILE" ]; then
  echo "$SHA  $FILE" | sha256sum --check
  exit 0
fi
if [ -z "${BLOODSKY_SOURCE_READ_TOKEN:-}" ]; then
  echo "::error::Original APK is in the archived private BLOODSKY-Android repo. Configure the BLOODSKY_SOURCE_READ_TOKEN Actions secret (fine-grained PAT scoped to that repo; Contents: Read-only), or supply a locally verified BLOODSKY_ORIGINAL_APK. No public source-APK fallback is allowed." >&2
  exit 1
fi
command -v gh >/dev/null || { echo "::error::GitHub CLI required to retrieve the archived private release" >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
GH_TOKEN="$BLOODSKY_SOURCE_READ_TOKEN" gh release download "$TAG" --repo "$SOURCE_REPO" --pattern "$ASSET" --dir "$tmp"
echo "$SHA  $tmp/$ASSET" | sha256sum --check
mv "$tmp/$ASSET" "$FILE"
echo "Pinned original retrieved from private archive and SHA-256 verified."
