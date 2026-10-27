#!/usr/bin/env bash
# Emulator smoke only: verify offline installation, launch, process stability and capture diagnostics.
# Real USB/Bluetooth/Modbus, licensing coverage, and cloud isolation remain separate gates.
set -euo pipefail
PACKAGE=ru.kascada.modbus
MAIN=ru.himik.nightscream.kascada.MainActivity
mkdir -p out/emulator

collect_diagnostics() {
  adb shell dumpsys activity activities > out/emulator/activities.txt 2>&1 || true
  adb shell dumpsys package "$PACKAGE" > out/emulator/package.txt 2>&1 || true
  adb logcat -d > out/emulator/logcat.txt 2>&1 || true
  adb logcat -d -s AndroidRuntime:E > out/emulator/runtime-errors.txt 2>&1 || true
  timeout 25 adb shell uiautomator dump /sdcard/bloodsky-ui.xml > out/emulator/ui-dump-command.txt 2>&1 || true
  adb pull /sdcard/bloodsky-ui.xml out/emulator/ui.xml > /dev/null 2>&1 || true
  adb shell screencap -p /sdcard/bloodsky.png > /dev/null 2>&1 || true
  adb pull /sdcard/bloodsky.png out/emulator/screenshot.png > /dev/null 2>&1 || true
}
trap collect_diagnostics EXIT

adb wait-for-device
adb shell getprop sys.boot_completed | grep -q 1
adb install -r -g out/BLOODSKY-QA.apk | tee out/emulator/install.txt
adb shell pm path "$PACKAGE" | tee out/emulator/pm-path.txt
adb shell pm grant "$PACKAGE" android.permission.READ_EXTERNAL_STORAGE || true
adb shell svc wifi disable || true
adb shell svc data disable || true
adb shell am force-stop "$PACKAGE" || true
adb logcat -c || true

adb shell am start -W -n "$PACKAGE/$MAIN" | tee out/emulator/launch.txt
sleep 10
adb shell pidof "$PACKAGE" | tee out/emulator/pid.txt
test -s out/emulator/pid.txt
adb shell dumpsys activity activities > out/emulator/activities-check.txt
grep -q "$PACKAGE" out/emulator/activities-check.txt

adb logcat -d -s AndroidRuntime:E > out/emulator/early-runtime-errors.txt
if grep -A 14 'FATAL EXCEPTION' out/emulator/early-runtime-errors.txt | grep -q "$PACKAGE"; then
  echo 'Fatal exception from BLOODSKY on emulator startup' >&2
  exit 1
fi

collect_diagnostics
trap - EXIT
if [ ! -s out/emulator/ui.xml ]; then
  echo 'UI hierarchy capture failed' >&2
  exit 1
fi
if ! grep -q "$PACKAGE" out/emulator/ui.xml; then
  echo 'Main activity not visible after permissions' >&2
  exit 1
fi
if grep -Eqi 'License:|Unlicensed' out/emulator/ui.xml; then
  echo 'Legacy license status is still visible in the main menu' >&2
  exit 1
fi
echo 'PASS: offline install and main menu without license label; not full acceptance.'
