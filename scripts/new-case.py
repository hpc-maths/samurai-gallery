#!/usr/bin/env python
"""Scaffold a new gallery case from the template.

    python scripts/new-case.py --category getting-started --slug my-case \
        --title "My case" --equation linear-advection

Creates cases/<category>/<slug>/ with case.yaml, README.md, main.cpp,
CMakeLists.txt and postprocess.py, ready to edit. Step 1 of "add a case in 3
steps": scaffold, fill in, open a PR.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "scripts" / "templates" / "case"
CASES = ROOT / "cases"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def render(text: str, subs: dict[str, str]) -> str:
    for key, value in subs.items():
        text = text.replace(key, value)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new samurai-gallery case.")
    parser.add_argument("--category", required=True, help="e.g. getting-started, hyperbolic, incompressible")
    parser.add_argument("--slug", required=True, help="kebab-case case id, e.g. kelvin-helmholtz")
    parser.add_argument("--title", required=True, help="human-readable title")
    parser.add_argument("--equation", default="TODO", help="equation slug, e.g. compressible-euler")
    parser.add_argument("--samurai-ref", default="main",
                        help="samurai git ref this case is tested against, e.g. v0.33.0")
    args = parser.parse_args()

    if not SLUG_RE.match(args.slug):
        parser.error("--slug must be kebab-case (lowercase letters, digits, dashes)")
    if not SLUG_RE.match(args.category):
        parser.error("--category must be kebab-case")

    dest = CASES / args.category / args.slug
    if dest.exists():
        parser.error(f"case already exists: {dest.relative_to(ROOT)}")

    subs = {
        "__TITLE__": args.title,
        "__SLUG__": args.slug,
        "__TARGET__": f"gallery-{args.slug}",
        "__EQUATION__": args.equation,
        "__SAMURAI_REF__": args.samurai_ref,
    }

    dest.mkdir(parents=True)
    for src in sorted(TEMPLATE.iterdir()):
        (dest / src.name).write_text(render(src.read_text(), subs))

    rel = dest.relative_to(ROOT)
    print(f"Created {rel}\n")
    print("Next steps:")
    print(f"  1. Edit {rel}/main.cpp  (the simulation)")
    print(f"  2. Edit {rel}/case.yaml (metadata + run profiles) and {rel}/README.md")
    print(f"  3. Test it locally:  bash infra/build_case.sh {rel} ci")
    print("  4. Commit and open a pull request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
