from __future__ import annotations

import sys


def progress(label: str, current: int, total: int) -> None:
    if total <= 0:
        total = 1
    width = 24
    done = min(width, max(0, round(width * current / total)))
    bar = "#" * done + "-" * (width - done)
    end = "\n" if current >= total else ""
    print(f"\r[{bar}] {current}/{total} {label}", file=sys.stderr, end=end, flush=True)
