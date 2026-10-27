#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
: "${BLOODSKY_ORIGINAL_APK:?Original APK path required}"
: "${ANDROID_HOME:?Android SDK required}"
TOOLS="$ANDROID_HOME/build-tools/35.0.0"
mkdir -p out
export BLOODSKY_UNSIGNED_APK="$ROOT/out/unsigned.apk"
export BLOODSKY_PATCH_LOG="$ROOT/out/patch-log.json"
python3 tools/dex_patch.py
"$TOOLS/zipalign" -f -p 4 out/unsigned.apk out/aligned.apk
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PASS="$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')"
keytool -genkeypair -noprompt -alias qa -keyalg RSA -keysize 3072 -validity 7 -dname "CN=BLOODSKY QA" -keystore "$TMP/key.p12" -storetype PKCS12 -storepass "$PASS" -keypass "$PASS" >/dev/null 2>&1
"$TOOLS/apksigner" sign --ks "$TMP/key.p12" --ks-type PKCS12 --ks-key-alias qa --ks-pass "pass:$PASS" --key-pass "pass:$PASS" --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --out out/BLOODSKY-QA.apk out/aligned.apk
unset PASS
"$TOOLS/apksigner" verify --verbose --print-certs out/BLOODSKY-QA.apk > out/signature-check.txt
sha256sum out/BLOODSKY-QA.apk > out/sha256.txt
