"""Reject invalid native coverage patches."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[3]
OVERLAY = ROOT / "spec/custom/isa/coverage_tools"
SCRIPT = ROOT / "tools/scripts/check_coverage_overlay.py"


@pytest.mark.parametrize(
    "change",
    [
        "bad_role",
        "empty_operand",
        "unknown_field",
        "unknown_operand_field",
        "missing_version",
        "empty",
        "invalid_path",
        "duplicate_yaml_key",
        "invalid_schema",
    ],
)
def test_invalid_overlay(tmp_path: Path, change: str) -> None:
    overlay = tmp_path / "overlay"
    shutil.copytree(OVERLAY, overlay)
    yaml = YAML()
    patches = sorted((overlay / "inst").rglob("*.yaml"))
    patch = next(p for p in patches if "operands" in yaml.load(p.read_text())["custom_semantics"])
    data = yaml.load(patch.read_text())
    facts = data["custom_semantics"]
    if change == "bad_role":
        next(iter(facts["operands"].values()))["role"] = "raed"
    elif change == "empty_operand":
        next(iter(facts["operands"].values())).clear()
    elif change == "unknown_operand_field":
        next(iter(facts["operands"].values()))["unexpected"] = "read"
    elif change == "unknown_field":
        facts["memroy_access"] = "none"
    elif change == "missing_version":
        del facts["version"]
    with patch.open("w") as stream:
        yaml.dump(data, stream)
    if change == "empty":
        shutil.rmtree(overlay / "inst")
    elif change == "invalid_path":
        patch.rename(overlay / "outside.yaml")
    elif change == "duplicate_yaml_key":
        with patch.open("a") as stream:
            stream.write("custom_semantics: {}\n")
    elif change == "invalid_schema":
        (overlay / "schema.json").write_text('{"type": "invalid"}')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(overlay)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 1
    assert "coverage overlay validation failed" in result.stderr
