#!/usr/bin/env python3
"""Validate overlay YAML files against schema.json."""

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "overlay", nargs="?", type=Path, default=ROOT / "spec/custom/isa/coverage_tools"
    )
    args = parser.parse_args()
    path = args.overlay / "schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    yaml = YAML(typ="safe")
    paths = sorted(
        path
        for path in args.overlay.rglob("*")
        if path.is_file() and path.suffix in {".yaml", ".yml"}
    )
    for path in paths:
        instruction = path.relative_to(args.overlay / "inst")
        source = ROOT / "spec/std/isa/inst" / instruction
        if not source.is_file():
            raise ValueError(f"missing instruction source: {source}")
        validator.validate(yaml.load(path.read_text(encoding="utf-8")))
    print(f"Validated {len(paths)} YAML files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
