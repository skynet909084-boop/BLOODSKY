#!/usr/bin/env bash
# On one Android 11 emulator, capture the untouched original and patched BLOODSKY
# with the same ru-RU locale, density, offline state and initial clean installation.
set -euo pipefail
PACKAGE=ru.kascada.modbus
MAIN=ru.himik.nightscream.kascada.MainActivity
mkdir -p out/visual
adb wait-for-device
adb shell svc wifi disable || true
adb shell svc data disable || true
capture() {
  local label="$1"
  for attempt in $(seq 1 40); do
    if adb shell pidof "$PACKAGE" >/dev/null 2>&1; then break; fi
    sleep 2
  done
  adb shell pidof "$PACKAGE" > "out/visual/${label}-pid.txt"
  sleep 3
  timeout 30 adb shell uiautomator dump "/sdcard/${label}.xml"
  adb pull "/sdcard/${label}.xml" "out/visual/${label}.xml"
  adb shell screencap -p "/sdcard/${label}.png"
  adb pull "/sdcard/${label}.png" "out/visual/${label}.png"
  test -s "out/visual/${label}.xml"
  test -s "out/visual/${label}.png"
}
launch_app() {
  local apk="$1" label="$2"
  adb install --no-incremental -r -g "$apk"
  local result=''
  for attempt in $(seq 1 40); do
    result="$(adb shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p "$PACKAGE" 2>/dev/null || true)"
    if [[ "$result" == *"$MAIN"* ]]; then break; fi
    sleep 2
  done
  [[ "$result" == *"$MAIN"* ]] || { echo "Activity unresolved for $label" >&2; exit 1; }
  adb shell am start -W -n "$PACKAGE/$MAIN" > "out/visual/${label}-launch.txt"
  grep -q 'Status: ok' "out/visual/${label}-launch.txt"
  capture "$label"
}
: "${BLOODSKY_ORIGINAL_APK:?Missing verified original APK path}"
test -s "$BLOODSKY_ORIGINAL_APK"
test -s out/BLOODSKY-QA.apk
launch_app "$BLOODSKY_ORIGINAL_APK" original
adb uninstall "$PACKAGE"
launch_app out/BLOODSKY-QA.apk bloodsky
python3 tests/compare_visual.py out/visual/original.png out/visual/original.xml out/visual/bloodsky.png out/visual/bloodsky.xml out/visual
echo "Original vs BLOODSKY Russian main menu comparison completed."
