#!/usr/bin/env bash
# Open the original HMI component palette on the active mbCanvas editor.
# Source: compatible base version 1.0.7 fragment_component_bar.xml (original component IDs).
set -euo pipefail
PACKAGE=ru.kascada.modbus
OUT=out/emulator/component-palette
mkdir -p "$OUT"
capture() {
  adb shell dumpsys activity activities > "$OUT/activities.txt" 2>&1 || true
  adb logcat -d -s AndroidRuntime:E > "$OUT/runtime-errors.txt" 2>&1 || true
  timeout 30 adb shell uiautomator dump /sdcard/bloodsky-component-palette.xml > "$OUT/uiautomator.txt" 2>&1 || true
  adb pull /sdcard/bloodsky-component-palette.xml "$OUT/ui.xml" > /dev/null 2>&1 || true
  adb shell screencap -p /sdcard/bloodsky-component-palette.png > /dev/null 2>&1 || true
  adb pull /sdcard/bloodsky-component-palette.png "$OUT/screen.png" > /dev/null 2>&1 || true
}
trap capture EXIT
adb shell pidof "$PACKAGE" > "$OUT/app.pid"
test -s "$OUT/app.pid"
adb shell dumpsys activity activities > "$OUT/before-activities.txt"
grep -q 'mbCanvas' "$OUT/before-activities.txt"
timeout 30 adb shell uiautomator dump /sdcard/bloodsky-palette-before.xml >/dev/null
adb pull /sdcard/bloodsky-palette-before.xml "$OUT/before.xml" >/dev/null
xy="$(python3 tests/find_ui_node.py "$OUT/before.xml" --resource-id "$PACKAGE:id/menu_bar_component")"
adb shell input tap $xy
sleep 4
capture
test -s "$OUT/ui.xml"
test -s "$OUT/screen.png"
# Fragments are comprised of the original component controls from fragment_component_bar.
# Assert the palette contains a representative setter, text and indicator.
python3 - "$OUT/ui.xml" <<'PY'
import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
ids={n.attrib.get('resource-id','').split('/')[-1] for n in root.iter('node')}
needed={'tab_switch','tab_button','tab_digital_setters','tab_text','tab_digital_indicator'}
missing=needed-ids
assert not missing, f'Original palette controls absent: {sorted(missing)}; observed={sorted(ids)}'
print('PASS: Original HMI palette contains setter, text, and indicator controls')
PY
# Toggle original component palette to FBD / logic components (from source fragment_component_logic_bar.xml).
xy="$(python3 tests/find_ui_node.py "$OUT/ui.xml" --resource-id "$PACKAGE:id/switch_layout")"
adb shell input tap $xy
sleep 3
timeout 30 adb shell uiautomator dump /sdcard/bloodsky-logic-palette.xml > "$OUT/logic-uiautomator.txt"
adb pull /sdcard/bloodsky-logic-palette.xml "$OUT/logic-ui.xml" > /dev/null
adb shell screencap -p /sdcard/bloodsky-logic-palette.png
adb pull /sdcard/bloodsky-logic-palette.png "$OUT/logic-screen.png" > /dev/null
test -s "$OUT/logic-ui.xml" && test -s "$OUT/logic-screen.png"
python3 - "$OUT/logic-ui.xml" <<'PY'
import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
ids={n.attrib.get('resource-id','').split('/')[-1] for n in root.iter('node')}
needed={'tab_var', 'tab_fb_rs', 'tab_fb_timer'}
missing=needed-ids
assert not missing,f'Original FBD palette missing: {sorted(missing)}; ids={sorted(ids)}'
print('PASS: FBD palette shows original variable, RS and timer components')
PY
if grep -A 12 'FATAL EXCEPTION' "$OUT/runtime-errors.txt" | grep -q "$PACKAGE"; then
  echo 'App crash after opening component palette' >&2
  exit 1
fi
trap - EXIT
echo 'PASS: HMI and FBD component palettes open in original editor; insert/save behavior still needs testing.'
