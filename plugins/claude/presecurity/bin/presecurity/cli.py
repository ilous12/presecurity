from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from .autofix import apply_autofix
from .doctor import print_doctor, run_doctor
from .i18n import t
from .scanner import plan_as_json, print_plan, scan
from .state import ensure_state, read_plan, state_paths, write_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="presecurity")
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Create .presecurity state files")
    sub.add_parser("scan", help="Scan project and write .presecurity/scan-plan.json")
    sub.add_parser("autofix", help="Apply safe fixes from the latest scan plan")
    sub.add_parser("cleanup", help="Remove .presecurity state files")
    sub.add_parser("doctor", help="Check presecurity environment and project state")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "init":
        paths = ensure_state(root)
        print(t("init.done", path=paths["dir"]))
        return 0

    if args.command == "scan":
        ensure_state(root)
        plan = scan(root)
        write_plan(root, plan)
        print(plan_as_json(plan) if args.json else print_plan(plan))
        return 1 if plan["summary"]["critical"] else 0

    if args.command == "autofix":
        ensure_state(root)
        plan = read_plan(root)
        if not plan.get("plan"):
            plan = scan(root)
            write_plan(root, plan)
        result = apply_autofix(root, plan)
        if args.json:
            import json

            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(t("autofix.title"))
            print(f"- {t('autofix.applied')}: {len(result['applied'])}")
            print(f"- {t('autofix.skipped')}: {len(result['skipped'])}")
            print(f"- {t('autofix.packages')}: {len(result['packages'])}")
            print(f"- {t('autofix.remaining')}: {result['remaining']['findings']}")
        return 0

    if args.command == "cleanup":
        paths = state_paths(root)
        if paths["dir"].exists():
            shutil.rmtree(paths["dir"])
        print(t("cleanup.done", path=paths["dir"]))
        return 0

    if args.command == "doctor":
        result = run_doctor(root)
        if args.json:
            import json

            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(print_doctor(result))
        return 0 if result["ok"] else 1

    return 2
