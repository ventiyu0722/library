#!/usr/bin/env python3
"""Migrate template IDs from A/B/C/D/E/F scheme to L/M/P scheme.

Updates: scores.json, evaluation-meta.json, test/results/ directories.
"""

import json
import os
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"

ID_MAP = {
    # L: 生活与娱乐 — 风格化
    "A01": "L01", "A02": "L02", "A03": "L03", "A04": "L04", "A05": "L05",
    "A06": "L06", "A07": "L07", "A08": "L08", "A09": "L09", "A10": "L10",
    "A11": "L11", "A12": "L12", "A13": "L13", "A14": "L14", "A15": "L15",
    "A16": "L16", "A17": "L17", "A18": "L18", "A19": "L19", "A20": "L20",
    "A21": "L21", "A22": "L22", "A23": "L23",
    # L: 生活与娱乐 — 写真/人像
    "B01": "L30", "B02": "L31", "B04": "L32", "B05": "L33",
    "B06": "L34", "B07": "L35",
    # L: 生活与娱乐 — 萌宠/宝宝
    "C01": "L50", "C02": "L51", "C03": "L52", "C04": "L53",
    "B03": "L54",
    # L: 生活与娱乐 — 换装/编辑
    "D01": "L60", "D02": "L61", "D03": "L62",
    # M: 日常工作与自媒体
    "E01": "M01", "E02": "M02", "E03": "M03", "E04": "M04", "E05": "M05",
    "E06": "M06", "E07": "M07", "E08": "M08",
    # P: 专业设计
    "F01": "P01", "F02": "P02", "F03": "P03", "F04": "P04",
    "F05": "P05", "F06": "P06", "F07": "P07", "F08": "P08",
}

CATEGORY_MAP = {
    "A": "L", "B": "L", "C": "L", "D": "L",
    "E": "M", "F": "P",
}


def migrate_scores():
    path = RESULTS_DIR / "scores.json"
    with open(path) as f:
        data = json.load(f)

    new_data = {}
    for key, val in data.items():
        if key == "_meta":
            new_data[key] = val
            continue
        new_key = ID_MAP.get(key, key)
        if isinstance(val, dict) and "category" in val:
            old_cat = val["category"]
            val["category"] = CATEGORY_MAP.get(old_cat, old_cat)
        new_data[new_key] = val
        if new_key != key:
            print(f"  scores: {key} -> {new_key}")

    with open(path, "w") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {path}")


def migrate_meta():
    path = RESULTS_DIR / "evaluation-meta.json"
    with open(path) as f:
        data = json.load(f)

    new_data = {}
    for key, val in data.items():
        new_key = ID_MAP.get(key, key)

        def update_entry(entry):
            if isinstance(entry, dict):
                if "template_id" in entry:
                    entry["template_id"] = ID_MAP.get(entry["template_id"], entry["template_id"])
                if "output" in entry and isinstance(entry["output"], str):
                    for old_id, new_id in ID_MAP.items():
                        entry["output"] = entry["output"].replace(f"/{old_id}/", f"/{new_id}/")
                        entry["output"] = entry["output"].replace(f"results/{old_id}/", f"results/{new_id}/")

        if isinstance(val, list):
            for item in val:
                update_entry(item)
        elif isinstance(val, dict):
            update_entry(val)

        new_data[new_key] = val
        if new_key != key:
            print(f"  meta: {key} -> {new_key}")

    with open(path, "w") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {path}")


def migrate_dirs():
    if not RESULTS_DIR.exists():
        print("No test/results/ directory found")
        return
    for old_id, new_id in ID_MAP.items():
        old_dir = RESULTS_DIR / old_id
        new_dir = RESULTS_DIR / new_id
        if old_dir.exists() and old_dir.is_dir():
            if new_dir.exists():
                print(f"  WARNING: {new_dir} already exists, merging")
                for f in old_dir.iterdir():
                    shutil.move(str(f), str(new_dir / f.name))
                old_dir.rmdir()
            else:
                old_dir.rename(new_dir)
            print(f"  dir: {old_id}/ -> {new_id}/")


if __name__ == "__main__":
    print("=== Migrating Template IDs ===")
    print("\n--- scores.json ---")
    migrate_scores()
    print("\n--- evaluation-meta.json ---")
    migrate_meta()
    print("\n--- test/results/ directories ---")
    migrate_dirs()
    print("\n=== Migration complete ===")
