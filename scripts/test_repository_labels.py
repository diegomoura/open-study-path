#!/usr/bin/env python3
"""Regression tests for intake-label provisioning."""

from __future__ import annotations

from ensure_repository_labels import ApiError, REQUIRED_LABELS, ensure_repository_labels


class FakeApi:
    def __init__(self, existing: set[str] | None = None, fail_status: int | None = None):
        self.existing = set(existing or set())
        self.fail_status = fail_status
        self.created: list[str] = []

    def __call__(self, method: str, path: str, payload: dict | None):
        if self.fail_status:
            raise ApiError(self.fail_status, "forced failure")
        if method == "GET":
            name = path.rsplit("/", 1)[-1].replace("%3A", ":")
            if name not in self.existing:
                raise ApiError(404, "missing")
            return {"name": name}
        if method == "POST":
            assert payload is not None
            name = payload["name"]
            self.existing.add(name)
            self.created.append(name)
            return payload
        raise AssertionError(f"unexpected method: {method}")


def main() -> None:
    fake = FakeApi()
    result = ensure_repository_labels("example/study", fake)
    if set(result["created"]) != set(REQUIRED_LABELS) or set(fake.created) != set(REQUIRED_LABELS):
        raise SystemExit(f"missing labels were not created: {result}")

    fake = FakeApi({"study-request"})
    result = ensure_repository_labels("example/study", fake)
    if result != {"existing": ["study-request"], "created": ["intake:imported"]}:
        raise SystemExit(f"existing labels were not reused: {result}")

    fake = FakeApi(set(REQUIRED_LABELS))
    result = ensure_repository_labels("example/study", fake)
    if result["created"]:
        raise SystemExit("idempotent provisioning created duplicate labels")

    try:
        ensure_repository_labels("invalid", FakeApi())
    except ValueError:
        pass
    else:
        raise SystemExit("invalid repository identifier was accepted")

    try:
        ensure_repository_labels("example/study", FakeApi(fail_status=403))
    except ApiError as error:
        if error.status != 403:
            raise
    else:
        raise SystemExit("non-404 API failure was swallowed")

    print("Repository label provisioning regressions passed.")


if __name__ == "__main__":
    main()
