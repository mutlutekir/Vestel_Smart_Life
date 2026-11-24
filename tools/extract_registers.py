#!/usr/bin/env python3
"""Rebuild custom_components/vestel_smart_life/appliances.py from the Smart Life app.

The app ships one sample document per appliance family (assets/demo_*.json). They list
the registers a unit reports (``commandName``), where a value sits inside a register
(``position``/``length``) and what each value means. This script keeps only those facts
and writes them as a small Python table; the documents themselves are not copied.

    python3 tools/extract_registers.py /path/to/apk/base/assets > appliances_table.py

Usage is only needed when the table has to be regenerated.
"""
from __future__ import annotations

import json
import pprint
import re
import sys
from pathlib import Path

FAMILIES = {
    "WM": ("demo_wm_t225.json", "demo_wm_t33t.json", "demo_wm_ic.json"),
    "WD": ("demo_wd.json",),
    "TD": ("demo_td.json",),
    "DW": ("demo_dw.json",),
    "OV": ("demo_ov.json",),
    "FD": ("demo_fd.json",),
}


def role(key: str) -> str:
    """'Refrigeration.X.Status.Door' -> 'Door'; keeps nested names like 'MeatProbe.DoorLock'."""
    for marker in ("Status.", "Setting.", "Error."):
        if marker in key:
            return key.split(marker, 1)[1]
    return key.split(".")[-1]


def label(text: str) -> str:
    m = re.fullmatch(r"M(\d+)", text)
    if m:
        return f"-{m.group(1)} °C"
    m = re.fullmatch(r"(\d+)C", text) or re.fullmatch(r"(\d+)Degree", text)
    if m:
        return f"{m.group(1)} °C"
    m = re.fullmatch(r"(\d+)Rpm", text)
    if m:
        return f"{m.group(1)} rpm"
    m = re.fullmatch(r"(\d+)Hours?", text)
    if m:
        return f"{m.group(1)} h"
    if text == "ColdDegree":
        return "Cold"
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)


def main(assets: Path) -> None:
    table: dict[str, dict] = {}
    for family, files in FAMILIES.items():
        registers: dict[tuple, dict] = {}
        bits: dict[str, dict[int, str]] = {}
        codes: dict[str, dict[int, str]] = {}
        for name in files:
            doc = json.loads((assets / name).read_text())
            for section in ("status", "settings"):
                for item in doc.get(section) or []:
                    reg = item.get("commandName")
                    if not reg:
                        continue
                    pos, length = item.get("position"), item.get("length")
                    kind = item.get("valueType")
                    key = (reg, pos, length, role(item["key"]) if kind == "Boolean" else None)
                    if kind == "Boolean":
                        # Pairs such as DoorOpen (0) / DoorClosed (1) describe one bit twice.
                        if item.get("commandValue", 1) != 1 or pos is None:
                            continue
                        registers[key] = {"reg": reg, "pos": pos, "len": length, "kind": "bool",
                                          "role": role(item["key"])}
                    elif kind == "Enum":
                        entry = registers.setdefault(key, {"reg": reg, "pos": pos, "len": length,
                                                           "kind": "enum", "role": role(item["key"]), "values": {}})
                        for v in item.get("values") or []:
                            if "commandValue" in v:
                                entry["values"].setdefault(v["commandValue"], label(v["value"].split(".")[-1]))
                    elif kind == "Integer":
                        lim = item.get("valueLimits") or {}
                        registers[key] = {"reg": reg, "pos": pos, "len": length, "kind": "int",
                                          "role": role(item["key"]), "unit": lim.get("unit"),
                                          "min": lim.get("min"), "max": lim.get("max")}
            for item in doc.get("errors") or []:
                reg, pos = item.get("commandName"), item.get("position")
                name = label(role(item["key"]).split(".")[-1])
                if reg and isinstance(pos, int):
                    if pos >= 0:  # one bit per error (ovens, fridge-freezers)
                        bits.setdefault(reg, {})[pos] = name
                elif reg and "commandValue" in item:  # one code per error (washers, dishwashers, dryers)
                    codes.setdefault(reg, {})[item["commandValue"]] = name
        table[family] = {
            "registers": sorted(registers.values(), key=lambda e: (e["reg"], e["pos"] or 0, e["role"])),
            "error_bits": {reg: sorted(b.items()) for reg, b in sorted(bits.items())},
            "error_codes": {reg: dict(sorted(c.items())) for reg, c in sorted(codes.items())},
        }
    pprint.pprint(table, width=110, sort_dicts=False)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
