from __future__ import annotations

from pathlib import Path
import re


TEST_PATH_PARTS = {"test", "tests", "__tests__", "spec", "fixtures", "fixture", "examples", "demo"}
PLACEHOLDER_WORDS = {
    "changeme",
    "change-me",
    "dummy",
    "example",
    "fake",
    "placeholder",
    "sample",
    "test",
    "todo",
    "xxx",
}


def is_false_positive(rule_id: str, rel: str, line: str, full_text: str) -> bool:
    lowered = line.lower()
    path_parts = {part.lower() for part in Path(rel).parts}
    if "presecurity: ignore" in lowered:
        return True
    if rule_id == "hardcoded-secret":
        return is_test_path(path_parts) or any(word in lowered for word in PLACEHOLDER_WORDS)
    if rule_id == "nextjs-public-secret":
        return any(word in lowered for word in PLACEHOLDER_WORDS)
    if rule_id == "docker-root-user":
        return bool(re.search(r"(?im)^USER\s+\S+", full_text))
    if rule_id == "express-state-changing-route":
        return any(token in lowered for token in ("requireauth", "authenticate", "authorize", "csrf"))
    if rule_id == "ssrf-unvalidated-url":
        return any(token in lowered for token in ("allowed", "allowlist", "trusted", "internal_only"))
    if rule_id == "sql-string-concat":
        return is_test_path(path_parts) or "presecurity: fixture" in lowered
    return False


def is_test_path(path_parts: set[str]) -> bool:
    return bool(path_parts & TEST_PATH_PARTS)
