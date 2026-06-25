from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Any

from .i18n import t


@dataclass(frozen=True)
class ChangedFile:
    path: str
    added: int
    removed: int
    hints: tuple[str, ...]


def analyze_intent(root: Path, base: str = "HEAD") -> dict[str, Any]:
    diff = git_diff(root, base)
    if not diff:
        return {
            "mode": "git-diff",
            "base": base,
            "available": False,
            "summary": t("intent.none"),
            "changedFiles": [],
            "securityHints": [],
        }

    changed = parse_changed_files(diff)
    hints = sorted({hint for item in changed for hint in item.hints})
    return {
        "mode": "git-diff",
        "base": base,
        "available": True,
        "summary": summarize_intent(changed, hints),
        "changedFiles": [
            {"path": item.path, "added": item.added, "removed": item.removed, "hints": list(item.hints)}
            for item in changed
        ],
        "securityHints": hints,
    }


def git_diff(root: Path, base: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "diff", "--unified=0", base, "--"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode not in (0, 1):
        return ""
    return completed.stdout


def parse_changed_files(diff: str) -> list[ChangedFile]:
    files: list[ChangedFile] = []
    current: str | None = None
    added = 0
    removed = 0
    added_lines: list[str] = []

    for line in diff.splitlines():
        if line.startswith("diff --git "):
            if current:
                files.append(build_changed_file(current, added, removed, added_lines))
            current = None
            added = 0
            removed = 0
            added_lines = []
            continue
        if line.startswith("+++ b/"):
            current = line.removeprefix("+++ b/")
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
            added_lines.append(line[1:])
            continue
        if line.startswith("-") and not line.startswith("---"):
            removed += 1

    if current:
        files.append(build_changed_file(current, added, removed, added_lines))
    return files


def build_changed_file(path: str, added: int, removed: int, added_lines: list[str]) -> ChangedFile:
    joined = "\n".join(added_lines)
    return ChangedFile(path=path, added=added, removed=removed, hints=tuple(classify_hints(path, joined)))


def classify_hints(path: str, text: str) -> list[str]:
    checks = [
        ("auth-flow", r"\b(auth|login|logout|session|jwt|oauth|permission|role|tenant)\b"),
        ("api-entrypoint", r"\b(GET|POST|PUT|DELETE|router\.|app\.|@Get|@Post|APIView|FastAPI|express)\b"),
        ("database-access", r"\b(select|insert|update|delete|findById|findOne|query|execute|save)\b"),
        ("outbound-http", r"\b(fetch|axios|requests\.|http\.Get|http\.Post|RestTemplate|WebClient)\b"),
        ("file-system", r"\b(open\(|readFile|writeFile|Path\.|File\(|os\.path|fs\.)\b"),
        ("shell-execution", r"\b(exec|spawn|subprocess|system|Runtime\.getRuntime)\b"),
        ("rendered-html", r"\b(innerHTML|dangerouslySetInnerHTML|template|render|markdown|html)\b"),
        ("ci-cd", r"\b(github\.|workflow|actions|secrets\.|pull_request_target)\b"),
        ("infrastructure", r"\b(resource|security_group|ingress|privileged|runAsRoot|cidr_blocks)\b"),
    ]
    haystack = f"{path}\n{text}"
    return [name for name, pattern in checks if re.search(pattern, haystack, flags=re.IGNORECASE)]


def summarize_intent(changed: list[ChangedFile], hints: list[str]) -> str:
    if not changed:
        return t("intent.no_changed")
    file_count = len(changed)
    added = sum(item.added for item in changed)
    removed = sum(item.removed for item in changed)
    if hints:
        return t("intent.with_hints", file_count=file_count, added=added, removed=removed, hints=", ".join(hints[:6]))
    return t("intent.without_hints", file_count=file_count, added=added, removed=removed)
