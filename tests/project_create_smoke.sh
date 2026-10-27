#!/usr/bin/env bash
# Optional deeper acceptance: create a local project and open the original editor offline.
set -euo pipefail
PACKAGE=ru.kascada.modbus
mkdir -p out/emulator/project
capture() {
  adb shell dumpsys activity activities > out/emulator/project/activities.txt 2>&1 || true
  adb logcat -d -s AndroidRuntime:E > out/emulator/project/runtime-errors.txt 2>&1 || true
  timeout 25 adb shell uiautomator dump /sdcard/project-ui.xml > /dev/null 2>&1 || true
  adb pull /sdcard/project-ui.xml out/emulator/project/ui.xml > /dev/null 2>&1 || true
  adb shell screencap -p /sdcard/project-screen.png > /dev/null 2>&1 || true
  adb pull /sdcard/project-screen.png out/emulator/project/screen.png > /dev/null 2>&1 || true
}
dump() {
  timeout 25 adb shell uiautomator dump /sdcard/project-ui.xml > /dev/null
  adb pull /sdcard/project-ui.xml out/emulator/project/ui.xml > /dev/null
}
tap_node() {
  local target="$1" mode="$2" xy
  if [ "$mode" = id ]; then
    xy="$(python3 tests/find_ui_node.py out/emulator/project/ui.xml --resource-id "$target")"
  else
    xy="$(python3 tests/find_ui_node.py out/emulator/project/ui.xml --class-name "$target")"
  fi
  adb shell input tap $xy
}
trap capture EXIT
dump
tap_node "$PACKAGE:id/bGoToCanvas" id
sleep 2
dump
tap_node 'android.widget.EditText' class
adb shell input text 'BLOODSKYQA'
adb shell input keyevent KEYCODE_BACK || true
sleep 1
dump
tap_node 'android:id/button1' id
sleep 8
capture
grep -q 'mbCanvas' out/emulator/project/activities.txt || { echo 'Project did not open the original editor' >&2; exit 1; }
test -s out/emulator/project/screen.png
if grep -A 14 'FATAL EXCEPTION' out/emulator/project/runtime-errors.txt | grep -q "$PACKAGE"; then
  echo 'App crashed creating local project' >&2
  exit 1
fi
trap - EXIT
echo 'PASS: created local project and reached original mbCanvas editor; persistence not yet verified.'
