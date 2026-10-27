#!/usr/bin/env bash
# Local physical-device smoke for BLOODSKY Beta 2. Never use an emulator.
set -euo pipefail
APK="$1"
SHA="7e2a823afaeb1c8255709fa4afa88963963e00fc61f06fe063c880ac725ffc71"
PACKAGE="ru.kascada.modbus"
ACTIVITY="ru.himik.nightscream.kascada.MainActivity"
OUT="out/physical-device-acceptance"
test -f "$APK"
command -v adb >/dev/null
command -v sha256sum >/dev/null
echo "$SHA  $APK" | sha256sum --check
if [ -z "$(printenv ANDROID_SERIAL || true)" ]; then
  COUNT="$(adb devices | awk '$2=="device"{n++}END{print n+0}')"
  test "$COUNT" -eq 1 || { echo "Connect exactly one authorized device (or set ANDROID_SERIAL)" >&2; exit 2; }
fi
adb wait-for-device
QEMU="$(adb shell getprop ro.kernel.qemu | tr -d '\r')"
HARDWARE="$(adb shell getprop ro.hardware | tr -d '\r')"
FINGERPRINT="$(adb shell getprop ro.build.fingerprint | tr -d '\r')"
case "$QEMU/$HARDWARE/$FINGERPRINT" in
  1/*|*ranchu*|*goldfish*|*sdk_gphone*|*generic_x86*|*emulator*) echo "FAIL: emulator; requires physical Android hardware." >&2; exit 2;;
esac
mkdir -p "$OUT"
{
  echo "status=IN_PROGRESS"
  echo "sha256=$SHA"
  echo "model=$(adb shell getprop ro.product.model | tr -d '\r')"
  echo "android=$(adb shell getprop ro.build.version.release | tr -d '\r')"
  echo "api=$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "emulator=false"
} > "$OUT/summary.txt"
capture() {
  adb shell screencap -p /sdcard/bloodsky-test.png >/dev/null 2>&1 || true
  adb pull /sdcard/bloodsky-test.png "$OUT/screen.png" >/dev/null 2>&1 || true
  timeout 30 adb shell uiautomator dump /sdcard/bloodsky-test.xml > "$OUT/uiautomator.txt" 2>&1 || true
  adb pull /sdcard/bloodsky-test.xml "$OUT/ui.xml" >/dev/null 2>&1 || true
  adb logcat -d -s AndroidRuntime:E > "$OUT/crashes.txt" 2>&1 || true
}
trap capture EXIT
# IMPORTANT: signature conflicts are not fixed by uninstalling (would delete project data).
if ! adb install -r -g "$APK" > "$OUT/install.txt" 2>&1; then
  cat "$OUT/install.txt" >&2
  echo "Back up existing projects before any manual reinstall!" >&2
  exit 1
fi
adb shell am force-stop "$PACKAGE" || true
adb shell am start -W -n "$PACKAGE/$ACTIVITY" | tee "$OUT/start.txt"
sleep 12
adb shell pidof "$PACKAGE" > "$OUT/pid.txt"
test -s "$OUT/pid.txt"
capture
test -s "$OUT/ui.xml"
test -s "$OUT/screen.png"
if grep -A 14 "FATAL EXCEPTION" "$OUT/crashes.txt" | grep -q "$PACKAGE"; then
 echo "FAIL: AndroidRuntime crash" >&2
 exit 1
fi
echo "status=AUTOMATED_PHYSICAL_SMOKE_PASS" >> "$OUT/summary.txt"
trap - EXIT
echo "PASS physical Android launch; projects/USB/Bluetooth/Wi-Fi still require manual tests"
