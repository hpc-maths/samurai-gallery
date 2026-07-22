# Contributing a case

Adding a case to the gallery is meant to be easy: **scaffold, fill in, open a
PR.** The continuous integration then validates, builds, runs and renders your
case automatically, and posts the generated media on the pull request.

## The 3 steps

```bash
# 1. Scaffold from the template
python scripts/new-case.py --category hyperbolic --slug kelvin-helmholtz \
    --title "Kelvin-Helmholtz instability" --equation compressible-euler

# 2. Fill in the generated files (see "Anatomy" below)

# 3. Test locally, then commit and open a pull request
bash infra/build_case.sh cases/hyperbolic/kelvin-helmholtz ci
```

## Anatomy of a case

A case is one directory `cases/<category>/<slug>/` containing exactly these
files:

| File | Purpose |
|------|---------|
| `case.yaml` | Metadata + run profiles. The single source of truth; validated against `infra/schema/case.schema.json`. |
| `README.md` | The explanation shown on the case page (Markdown + LaTeX). |
| `main.cpp` | The simulation. Displayed with syntax highlighting, read directly from this file. |
| `CMakeLists.txt` | Build recipe. Always `find_package(samurai CONFIG REQUIRED)`; never vendor samurai. |
| `postprocess.py` | Turns the `.h5` output into `thumbnail.png` + `preview.mp4` using the shared `galleria` library. |

Generated media (`thumbnail.png`, `preview.mp4`) are **not committed**: they are
rendered in CI and deployed with the site.

## `case.yaml` essentials

- `methods`, `equation`, `dimension`, `adaptation` drive the website filters.
- `run.target` must match the target name in `CMakeLists.txt`.
- `run.output_prefix` must match the `--filename` prefix your `main.cpp` writes.
- Run profiles:
  - `ci`: fast, low-resolution run used to generate the preview media in CI.
  - `hero`: optional high-resolution run.
  - `args` lists CLI arguments **except** `--path`, `--filename` and
    `--nfiles`, which the build driver supplies.

## Conventions for `main.cpp`

- Use samurai's native CLI options (`--min-level`, `--max-level`, `--mr-eps`,
  ...); do not re-declare them.
- Write one output file per frame named `<prefix>_<frame:04d>` via
  `samurai::save(path, name, mesh, field)` (the flat leaf mesh, no debug flags).
- Keep it standalone and reproducible; pin behaviour through CLI args, not
  hard-coded machine specifics.

## Local requirements

Everything runs inside the dedicated `samurai-gallery` environment
(`environment.yml`) with samurai installed into it. See the README quick start.

## What CI checks

1. `python infra/validate.py` - schema + required files for every case.
2. Build + run the `ci` profile of changed cases.
3. Render media and attach a preview to the PR.
