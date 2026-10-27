#!/usr/bin/env bash
# Android 11 emulator-only: apply Russian locale before installing BLOODSKY.
set -euo pipefail
mkdir -p out/emulator
adb wait-for-device
adb shell getprop ro.product.locale > out/emulator/default-system-locale.txt
adb root
adb wait-for-device
adb shell 'setprop persist.sys.locale ru-RU; stop; sleep 2; start' || true
adb wait-for-device
for i in $(seq 1 90); do
  current="$(adb shell getprop persist.sys.locale 2>/dev/null | tr -d '\r' || true)"
  zygote="$(adb shell getprop init.svc.zygote 2>/dev/null | tr -d '\r' || true)"
  if [ "$current" = 'ru-RU' ] && [ "$zygote" = running ] && adb shell cmd package list packages 2>/dev/null | grep -q '^package:android$'; then
    echo "ru-RU" | tee out/emulator/selected-locale.txt
    echo 'PASS: emulator locale is ru-RU'
    exit 0
  fi
  sleep 2
done
echo 'Failed to switch emulator to ru-RU or Android framework not ready' >&2
exit 1
