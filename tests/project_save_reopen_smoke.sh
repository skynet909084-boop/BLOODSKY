#!/usr/bin/env bash
# Source-backed persistence probe: save project, find it in saved-project list, reopen editor.
set -euo pipefail
PACKAGE=ru.kascada.modbus
MAIN=ru.himik.nightscream.kascada.MainActivity
PROJECT=BLOODSKYQA
mkdir -p out/emulator/persistence
capture() {
  adb shell dumpsys activity activities > out/emulator/persistence/activities.txt 2>&1 || true
  adb logcat -d -s AndroidRuntime:E > out/emulator/persistence/runtime-errors.txt 2>&1 || true
  timeout 25 adb shell uiautomator dump /sdcard/persistence-ui.xml > /dev/null 2>&1 || true
  adb pull /sdcard/persistence-ui.xml out/emulator/persistence/ui.xml > /dev/null 2>&1 || true
  adb shell screencap -p /sdcard/persistence.png > /dev/null 2>&1 || true
  adb pull /sdcard/persistence.png out/emulator/persistence/screen.png > /dev/null 2>&1 || true
}
dump_ui() {
  timeout 25 adb shell uiautomator dump /sdcard/persistence-ui.xml > /dev/null
  adb pull /sdcard/persistence-ui.xml out/emulator/persistence/ui.xml > /dev/null
}
tap_id() {
  local xy
  xy="$(python3 tests/find_ui_node.py out/emulator/persistence/ui.xml --resource-id "$1")"
  adb shell input tap $xy
}
trap capture EXIT

# The previous smoke must have created BLOODSKYQA in the original editor.
adb shell input keyevent KEYCODE_BACK
sleep 2
dump_ui
tap_id "$PACKAGE:id/exit_yes"
sleep 4
adb shell am start -W -n "$PACKAGE/$MAIN" > out/emulator/persistence/back-to-main.txt
sleep 2
dump_ui
tap_id "$PACKAGE:id/button3"
sleep 3
dump_ui
cp out/emulator/persistence/ui.xml out/emulator/persistence/saved-project-list.xml
if ! grep -q "$PROJECT" out/emulator/persistence/saved-project-list.xml; then
  echo 'Saved project missing in original project load list' >&2
  exit 1
fi
xy="$(python3 tests/find_ui_node.py out/emulator/persistence/ui.xml --text-contains "$PROJECT")"
adb shell input tap $xy
sleep 8
capture
grep -q 'mbCanvas' out/emulator/persistence/activities.txt || {
  echo 'Saved project did not reopen original mbCanvas editor' >&2
  exit 1
}
if grep -A 14 'FATAL EXCEPTION' out/emulator/persistence/runtime-errors.txt | grep -q "$PACKAGE"; then
 echo 'Android app crashed in project save and reopen' >&2; exit 1
fi
trap - EXIT
echo 'PASS: local project appears in saved projects and reopens into mbCanvas; editor content roundtrip not verified.'
