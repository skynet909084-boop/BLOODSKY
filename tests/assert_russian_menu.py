#!/usr/bin/env python3
"""Check rendered Android main-menu labels via UiAutomator hierarchy.

Original KaScada UI renders some translations in all caps. Unicode casefold
avoids a false-negative from a literal mixed-case grep.
"""
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit("Usage: assert_russian_menu.py out/emulator/ui.xml")

expected = {
    "bGoToCanvas": "создать новый проект",
    "button3": "загрузить проект",
    "button4": "удалить проект",
    "btnExport": "экспорт проекта",
    "btnImport": "импорт проекта",
    "button2": "выход",
}
root = ET.parse(sys.argv[1]).getroot()
ui = {
    node.attrib.get("resource-id", "").rsplit("/", 1)[-1]: node.attrib.get("text", "").strip()
    for node in root.iter("node")
    if node.attrib.get("resource-id")
}

errors = [
    f"{rid}: expected {label!r}, received {ui.get(rid)!r}"
    for rid, label in expected.items()
    if ui.get(rid, "").casefold() != label.casefold()
]
if errors:
    raise SystemExit("FAIL Russian main-menu localization:\n" + "\n".join(errors))
if any(
    "unlicensed" in value.casefold() or "license:" in value.casefold()
    for value in ui.values()
):
    raise SystemExit("FAIL legacy license text is still visible")
print("PASS: all 6 main-menu commands are in Russian, legacy license hidden")
