#!/usr/bin/env bash
set -euo pipefail
mkdir -p out/emulator
adb install -r out/BLOODSKY-QA.apk
adb shell svc wifi disable || true
adb shell svc data disable || true
adb shell monkey -p ru.kascada.modbus -c android.intent.category.LAUNCHER 1 > out/emulator/launch.txt
sleep 12
adb shell pidof ru.kascada.modbus > out/emulator/pid.txt
adb shell screencap -p /sdcard/test.png
adb pull /sdcard/test.png out/emulator/test.png
adb logcat -d -s AndroidRuntime:E > out/emulator/crash.txt
test -s out/emulator/pid.txt && test -s out/emulator/test.png
if grep -A 12 'FATAL EXCEPTION' out/emulator/crash.txt | grep -q ru.kascada.modbus; then exit 1; fi
