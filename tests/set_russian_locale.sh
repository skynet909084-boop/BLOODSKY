#!/usr/bin/env bash
# Test that the untouched original Russian translations are used on the Android 11 emulator.
# Changes only the TEST DEVICE locale. Does not force Russian on users' phones.
set -euo pipefail
mkdir -p out/emulator
adb wait-for-device
adb shell getprop ro.product.locale | tee out/emulator/default-system-locale.txt
adb root
adb wait-for-device
# Official Android localization test approach: set persistent locale and restart framework.
# adb shell can disconnect while zygote is restarting; this is expected.
adb shell 'setprop persist.sys.locale ru-RU; stop; sleep 5; start' || true
adb wait-for-device
for i in $(seq 1 90); do
  current="$(adb shell getprop persist.sys.locale 2>/dev/null | tr -d '\r' || true)"
  zygote="$(adb shell getprop init.svc.zygote 2>/dev/null | tr -d '\r' || true)"
  if [ "$current" = ru-RU ] && [ "$zygote" = running ]; then break; fi
  sleep 2
done
current="$(adb shell getprop persist.sys.locale | tr -d '\r')"
echo "Selected locale: $current" | tee out/emulator/selected-locale.txt
test "$current" = ru-RU
adb shell am force-stop com.android.settings 2>/dev/null || true
echo "PASS: Android system requested ru-RU; UI strings will be checked after app launch"
