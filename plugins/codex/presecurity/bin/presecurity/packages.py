from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any


PACKAGE_FIXES = {
    "react_safe_html_sanitizer": {
        "ecosystem": "npm",
        "packages": ["dompurify"],
        "devPackages": ["@types/dompurify"],
    }
}


def collect_package_requirements(applied: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    requirements: list[dict[str, Any]] = []
    for item in applied:
        fix = item.get("fix")
        if fix not in PACKAGE_FIXES or fix in seen:
            continue
        seen.add(fix)
        requirements.append(PACKAGE_FIXES[fix])
    return requirements


def install_required_packages(root: Path, requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    npm_packages: list[str] = []
    npm_dev_packages: list[str] = []
    for requirement in requirements:
        if requirement["ecosystem"] == "npm":
            npm_packages.extend(requirement.get("packages", []))
            npm_dev_packages.extend(requirement.get("devPackages", []))
    if npm_packages or npm_dev_packages:
        results.extend(install_npm(root, sorted(set(npm_packages)), sorted(set(npm_dev_packages))))
    return results


def install_npm(root: Path, packages: list[str], dev_packages: list[str]) -> list[dict[str, Any]]:
    if not (root / "package.json").exists():
        return [{"ecosystem": "npm", "ok": False, "reason": "package.json not found"}]
    manager = detect_node_manager(root)
    results: list[dict[str, Any]] = []
    if packages:
        results.append(run_install(root, manager, packages, dev=False))
    if dev_packages:
        results.append(run_install(root, manager, dev_packages, dev=True))
    return results


def detect_node_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    return "npm"


def run_install(root: Path, manager: str, packages: list[str], dev: bool) -> dict[str, Any]:
    if manager == "pnpm":
        command = ["pnpm", "add", *packages]
        if dev:
            command.insert(2, "-D")
    elif manager == "yarn":
        command = ["yarn", "add", *packages]
        if dev:
            command.insert(2, "-D")
    else:
        command = ["npm", "install", *packages]
        if dev:
            command.insert(2, "--save-dev")
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    return {
        "ecosystem": "npm",
        "manager": manager,
        "packages": packages,
        "dev": dev,
        "ok": completed.returncode == 0,
        "command": " ".join(command),
        "stderr": completed.stderr[-1000:],
    }
