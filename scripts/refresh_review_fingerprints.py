#!/usr/bin/env python3
"""Check or refresh current SHA-256 entries in generated-artifact review manifests."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "state" / "reviews"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def process_manifest(path: Path, write: bool) -> tuple[int, int]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    artifacts = data.get("artifacts") or []
    stale = 0
    changed = 0
    for artifact in artifacts:
        if artifact.get("change") != "current":
            continue
        relative = artifact.get("path")
        recorded = artifact.get("sha256")
        if not isinstance(relative, str) or not isinstance(recorded, str):
            continue
        target = (ROOT / relative).resolve()
        if ROOT not in target.parents or not target.is_file():
            continue
        current = digest(target)
        if current != recorded:
            stale += 1
            print(f"STALE {path.relative_to(ROOT)}: {relative}: {recorded} -> {current}")
            if write:
                artifact["sha256"] = current
                changed += 1
    if changed:
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return stale, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="update all stale current fingerprints in one batch")
    args = parser.parse_args()
    if not REVIEWS.exists():
        print("No state/reviews directory; nothing to refresh.")
        return 0
    stale = changed = 0
    for manifest in sorted(REVIEWS.glob("*.yml")):
        manifest_stale, manifest_changed = process_manifest(manifest, args.write)
        stale += manifest_stale
        changed += manifest_changed
    if args.write:
        print(f"Refreshed {changed} fingerprint(s) in one batch.")
        return 0
    if stale:
        print(f"ERROR: {stale} stale review fingerprint(s). Run: python scripts/refresh_review_fingerprints.py --write")
        return 1
    print("Review fingerprints are current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
