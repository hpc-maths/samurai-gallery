#!/usr/bin/env python
"""Emit shell variable assignments for a case profile.

Usage: case_meta.py <case.yaml> <profile>
Prints TARGET, OUTPUT_PREFIX, NFILES, ARGS as quoted shell assignments so a
driver script can `eval` them.
"""

import shlex
import sys

import yaml


def main(yaml_path: str, profile: str) -> None:
    with open(yaml_path) as f:
        meta = yaml.safe_load(f)

    run = meta["run"]
    profiles = run["profiles"]
    if profile not in profiles:
        # fall back to ci if the requested profile is not defined
        profile = "ci"
    prof = profiles[profile]

    args = " ".join(shlex.quote(str(a)) for a in prof.get("args", []))
    print(f"TARGET={shlex.quote(run['target'])}")
    print(f"OUTPUT_PREFIX={shlex.quote(run['output_prefix'])}")
    print(f"NFILES={shlex.quote(str(prof['nfiles']))}")
    print(f"ARGS={shlex.quote(args)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
