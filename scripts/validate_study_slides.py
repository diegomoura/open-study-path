#!/usr/bin/env python3
"""Validate reusable study-slide contracts and generated offline ZIP artifacts."""
from pathlib import Path
import sys
from study_slides import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    result = validate_repository(ROOT)
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Study-slide HTML, independent review and offline ZIP contract passed.")


if __name__ == "__main__":
    main()
