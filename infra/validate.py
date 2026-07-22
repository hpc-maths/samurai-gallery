#!/usr/bin/env python
"""Validate every gallery case against the schema and the on-disk contract.

Run from the repo root:  python infra/validate.py
Exits non-zero if any case is invalid. Used by the `validate` CI job.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "infra" / "schema" / "case.schema.json"
CASES_DIR = ROOT / "cases"

# Files every case directory must contain besides case.yaml.
REQUIRED_FILES = ["main.cpp", "CMakeLists.txt", "README.md", "postprocess.py"]
# Engine-based cases build from an external project, so they replace
# main.cpp/CMakeLists.txt with the engine + a displayed code_file.
ENGINE_REQUIRED_FILES = ["README.md", "postprocess.py"]


def validate_case(case_yaml: Path, validator: Draft7Validator) -> list[str]:
    errors: list[str] = []
    rel = case_yaml.parent.relative_to(ROOT)

    try:
        meta = yaml.safe_load(case_yaml.read_text())
    except yaml.YAMLError as exc:
        return [f"{rel}: invalid YAML ({exc})"]

    for err in sorted(validator.iter_errors(meta), key=lambda e: e.path):
        loc = "/".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{rel}: schema: {loc}: {err.message}")

    engine = meta.get("engine") if isinstance(meta, dict) else None
    required = ENGINE_REQUIRED_FILES if engine else REQUIRED_FILES
    for fname in required:
        if not (case_yaml.parent / fname).exists():
            errors.append(f"{rel}: missing required file '{fname}'")

    if engine and isinstance(engine, dict) and "code_file" in engine:
        if not (case_yaml.parent / engine["code_file"]).exists():
            errors.append(f"{rel}: engine.code_file '{engine['code_file']}' not found")

    # Local cases must pin the samurai version they are tested against; engine
    # cases pin samurai through their engine environment instead.
    if not engine:
        samurai = meta.get("samurai") if isinstance(meta, dict) else None
        if not (isinstance(samurai, dict) and samurai.get("ref")):
            errors.append(f"{rel}: missing 'samurai.ref' (samurai version this case is tested against)")

    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    case_files = sorted(CASES_DIR.glob("*/*/case.yaml"))
    if not case_files:
        print("no cases found under cases/*/*/case.yaml", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for case_yaml in case_files:
        all_errors.extend(validate_case(case_yaml, validator))

    if all_errors:
        print("INVALID cases:\n")
        for e in all_errors:
            print(f"  - {e}")
        print(f"\n{len(all_errors)} error(s) across {len(case_files)} case(s).")
        return 1

    print(f"OK: {len(case_files)} case(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
