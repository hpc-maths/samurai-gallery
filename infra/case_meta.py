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
    engine = meta.get("engine") or {}
    samurai = meta.get("samurai") or {}

    print(f"TARGET={shlex.quote(run['target'])}")
    print(f"OUTPUT_PREFIX={shlex.quote(run['output_prefix'])}")
    print(f"OUTPUT_SUBDIR={shlex.quote(run.get('output_subdir', ''))}")
    print(f"NFILES={shlex.quote(str(prof['nfiles']))}")
    print(f"ARGS={shlex.quote(args)}")

    if engine:
        # Engine cases build from an external git project in their own env,
        # which also provides samurai.
        print(f"IS_ENGINE={shlex.quote('1')}")
        print(f"ENV={shlex.quote(engine['env'])}")
        print(f"ENGINE_REPO={shlex.quote(engine['repo'])}")
        print(f"ENGINE_REF={shlex.quote(engine['ref'])}")
        print("SAMURAI_REPO=''")
        print("SAMURAI_REF=''")
    else:
        # Local cases build against a samurai installed at the declared ref.
        print("IS_ENGINE=''")
        print(f"ENV={shlex.quote(meta.get('env', 'samurai-gallery'))}")
        print("ENGINE_REPO=''")
        print("ENGINE_REF=''")
        print(f"SAMURAI_REPO={shlex.quote(samurai.get('repo', 'hpc-maths/samurai'))}")
        print(f"SAMURAI_REF={shlex.quote(samurai['ref'])}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
