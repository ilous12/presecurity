from pathlib import Path

from presecurity.autofix import apply_autofix
from presecurity.scanner import scan


def test_scan_detects_yaml_and_eval(tmp_path: Path):
    (tmp_path / "app.py").write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    (tmp_path / "app.js").write_text("eval(input)\n", encoding="utf-8")

    plan = scan(tmp_path)

    rule_ids = {finding["ruleId"] for finding in plan["findings"]}
    assert "python-yaml-unsafe-load" in rule_ids
    assert "javascript-eval" in rule_ids


def test_autofix_applies_safe_yaml_fix(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    plan = scan(tmp_path)

    result = apply_autofix(tmp_path, plan)

    assert result["applied"]
    assert "yaml.safe_load" in target.read_text(encoding="utf-8")
