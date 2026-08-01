#!/usr/bin/env python3
from pathlib import Path


def require(path: str, terms: list[str]) -> None:
    text = Path(path).read_text(encoding="utf-8")
    missing = [term for term in terms if term not in text]
    if missing:
        raise SystemExit(f"{path} missing: {', '.join(missing)}")


def main() -> None:
    require(
        "instructions/03-await-ci-and-merge.md",
        [
            "Prefer auto-merge",
            "bounded backoff",
            "median of the last 5 successful runs",
            "minimum observation budget: 3 minutes",
            "normal maximum observation budget: 15 minutes",
            "Do not provide the next lifecycle command",
        ],
    )
    require(
        "instructions/28-propose-path.md",
        [
            "instructions/03-await-ci-and-merge.md",
            "Do not end the learner interaction merely because CI is still running",
            "mark the PR ready, merge it and verify the default branch",
        ],
    )
    print("Proposal completion wait regression passed.")


if __name__ == "__main__":
    main()
