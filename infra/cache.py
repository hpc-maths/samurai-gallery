#!/usr/bin/env python
"""Content-addressed cache key for a rendered gallery case.

A case's media (thumbnail-*.png / preview-*.mp4) are a pure function of a small
set of inputs. This module hashes those inputs into a stable key so the build
driver can skip compile+run+render when nothing that affects the output has
changed.

Inputs that make up the key:
  - the run profile (ci / hero);
  - the pinned samurai/engine version - the `samurai` block (repo + ref) for
    local cases, the `engine` block (repo + ref + env) for engine cases - taken
    straight from case.yaml. The ref is the version identity used throughout the
    gallery (ensure_samurai.sh caches installs per ref), so bumping it here
    invalidates the media, matching how the case is actually rebuilt;
  - the case's own source files (main.cpp / scenario.hpp, CMakeLists.txt,
    postprocess.py, any extra headers), excluding build and output artefacts and
    the generated media themselves;
  - the shared figure-building engine and scripts: infra/galleria/*.py,
    infra/case_meta.py, infra/build_case.sh.

Usage:
    python infra/cache.py key      <case-dir> <profile>   # print the hex key
    python infra/cache.py manifest <case-dir> <profile>   # print JSON manifest
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Directories never hashed (build/run artefacts, caches).
_SKIP_DIRS = {".output", "build", "build-engine", "__pycache__", ".git"}
# Generated media are outputs, not inputs.
_MEDIA_SUFFIXES = (".png", ".mp4", ".gif")
_MEDIA_PREFIXES = ("thumbnail", "preview")
# Case files that affect only the website (rebuilt on every deploy), never the
# media, so they must not force an expensive re-run. case.yaml is excluded here
# because only its run/engine config is key-relevant (hashed separately below).
_CASE_FILES_IGNORED = {"README.md", "case.yaml"}

# Shared figure-building engine + scripts, relative to ROOT.
_SHARED_INPUTS = [
    "infra/galleria/__init__.py",
    "infra/galleria/h5.py",
    "infra/galleria/render.py",
    "infra/case_meta.py",
    "infra/build_case.sh",
]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_media(name: str) -> bool:
    return name.endswith(_MEDIA_SUFFIXES) and name.startswith(_MEDIA_PREFIXES)


def _case_files(case_dir: Path) -> dict[str, str]:
    """Hash every source file in the case dir, keyed by 'case/<relpath>'."""
    files: dict[str, str] = {}
    for path in sorted(case_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(case_dir)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue
        if _is_media(path.name):
            continue
        if rel.as_posix() in _CASE_FILES_IGNORED:
            continue
        files[f"case/{rel.as_posix()}"] = _sha256_file(path)
    return files


def _run_config(meta: dict, profile: str) -> dict:
    """The key-relevant slice of case.yaml: what drives the run and render.

    Deliberately excludes site-only metadata (title, tags, summary, ...) and
    unrelated profiles, so editing prose or the 'hero' profile does not
    invalidate the cached 'ci' media.
    """
    run = meta["run"]
    profiles = run.get("profiles", {})
    prof = profiles.get(profile) or profiles.get("ci", {})
    return {
        "target": run.get("target"),
        "output_prefix": run.get("output_prefix"),
        "output_subdir": run.get("output_subdir", ""),
        "env": meta.get("env", "samurai-gallery"),
        # Version identity: exactly one of these is populated per case.
        "samurai": meta.get("samurai") or {},
        "engine": meta.get("engine") or {},
        "args": prof.get("args", []),
        "nfiles": prof.get("nfiles"),
    }


def _shared_files() -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in _SHARED_INPUTS:
        path = ROOT / rel
        if path.is_file():
            files[rel] = _sha256_file(path)
    return files


def build_inputs(case_dir: Path, profile: str) -> dict:
    """The canonical, key-determining inputs for a case+profile."""
    meta = yaml.safe_load((case_dir / "case.yaml").read_text())
    return {
        "profile": profile,
        "engine": bool(meta.get("engine")),
        "run": _run_config(meta, profile),
        "files": {**_case_files(case_dir), **_shared_files()},
    }


def compute_key(inputs: dict) -> str:
    canonical = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[0] not in {"key", "manifest"}:
        print(__doc__, file=sys.stderr)
        return 2
    command, case_arg, profile = argv
    case_dir = Path(case_arg).resolve()
    inputs = build_inputs(case_dir, profile)

    if command == "key":
        print(compute_key(inputs))
    else:  # manifest
        manifest = {
            "key": compute_key(inputs),
            "case": case_dir.name,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "inputs": inputs,
        }
        print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
