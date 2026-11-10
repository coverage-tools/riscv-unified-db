#!/usr/bin/env python3
"""Validate native coverage semantics patches."""

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

ROOT = Path(__file__).resolve().parents[2]
INSTRUCTION = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9_.-]*\.yaml")


def _local_references(value: object) -> bool:
    if isinstance(value, dict):
        return all(
            key != "$dynamicRef"
            and (key != "$ref" or (isinstance(child, str) and child.startswith("#/$defs/")))
            and _local_references(child)
            for key, child in value.items()
        )
    return not isinstance(value, list) or all(_local_references(child) for child in value)


def expanded_overlay(overlay: Path) -> dict[str, dict]:
    schema = json.loads((overlay / "schema.json").read_text(encoding="utf-8"))
    if not _local_references(schema):
        raise ValueError("overlay schema references must stay within $defs")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    patches = sorted(overlay.rglob("*.yaml"))
    if not patches:
        raise ValueError(f"no overlay patches found in {overlay}")
    yaml = YAML(typ="safe")
    result = {}
    for patch in patches:
        if patch.is_symlink() or not patch.resolve().is_relative_to(overlay.resolve()):
            raise ValueError(f"overlay symlink is unsupported: {patch}")
        data = yaml.load(patch.read_text(encoding="utf-8"))
        error = next(validator.iter_errors(data), None)
        if error is not None:
            raise ValueError(f"{patch}: {error.message}")
        relative = patch.relative_to(overlay)
        instruction = relative.as_posix().removeprefix("inst/")
        if relative.parts[0] != "inst" or not INSTRUCTION.fullmatch(instruction):
            raise ValueError(f"unsupported overlay file: {patch}")
        if "custom_semantics" not in data:
            raise ValueError(f"expected native instruction patch: {patch}")
        result[instruction] = data
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "overlay", nargs="?", type=Path, default=ROOT / "spec/custom/isa/coverage_tools"
    )
    args = parser.parse_args()
    try:
        count = len(expanded_overlay(args.overlay))
    except (OSError, ValueError, KeyError, SchemaError, YAMLError) as error:
        print(f"coverage overlay validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {count} coverage overlay patches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
