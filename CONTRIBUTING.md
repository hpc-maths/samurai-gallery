# Contributing a case

Adding a case to the gallery is meant to be easy: **scaffold, fill in, open a
PR.** The continuous integration then validates, builds, runs and renders your
case automatically, and posts the generated media on the pull request.

## The 3 steps

```bash
# 1. Scaffold from the template
python scripts/new-case.py --category hyperbolic --slug kelvin-helmholtz \
    --title "Kelvin-Helmholtz instability" --equation compressible-euler \
    --samurai-ref v0.33.0

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

## Pinning the samurai version

Every case records the samurai version it is tested against, so CI builds and
links the case against **that exact version** (and the site shows it as
"Tested with samurai `<ref>`"). Cases sharing a ref reuse a single build.

```yaml
samurai:
  repo: hpc-maths/samurai   # optional, default hpc-maths/samurai
  ref: v0.33.0              # required: tag, commit or branch
```

Bump `ref` when you validate a case against a newer samurai; different cases may
pin different versions.

## Engine cases (external solver)

A case powered by an external solver (e.g. `samurai-euler`) has no `main.cpp`.
Instead of the `samurai` block it declares a self-describing `engine` block -
the git repository, the tested ref, the build/run environment and the source
file to display. CI clones the repo at that ref, creates the environment from
its `conda/environment.yml` if missing, and builds `run.target`:

```yaml
engine:
  repo: hpc-maths/samurai-euler   # git repository
  ref: main                       # tested ref
  env: samurai-euler-env          # conda env (provides samurai for this case)
  code_file: scenario.hpp         # source shown on the site
```

## Conventions for `main.cpp`

- Use samurai's native CLI options (`--min-level`, `--max-level`, `--mr-eps`,
  ...); do not re-declare them.
- Write one output file per frame named `<prefix>_<frame:04d>` via
  `samurai::save(path, name, mesh, field)` (the flat leaf mesh, no debug flags).
- Keep it standalone and reproducible; pin behaviour through CLI args, not
  hard-coded machine specifics.

## Local requirements

Everything runs inside the dedicated `samurai-gallery` environment
(`environment.yml`), which provides the build toolchain and samurai's
dependencies. `infra/build_case.sh` builds the samurai version pinned by the
case into a per-ref cache under `~/.cache/samurai-gallery` and links the case
against it - you do not install samurai into the environment yourself. See the
README quick start.

## Media cache

`build_case.sh` skips compile+run+render when nothing that affects a case's
media has changed. It computes a content-addressed key (`infra/cache.py`) from
the case's pinned samurai/engine version (the `samurai`/`engine` block in
`case.yaml`), the case sources (`main.cpp`/`scenario.hpp`/`CMakeLists.txt` and
the `run` config), the shared figure engine (`infra/galleria/`), and its
`postprocess.py`. On a hit the media are restored from the store
(`.cache/media/`, gitignored); on a miss the case is built and the store is
repopulated. Site-only metadata (title, tags, `README.md`) and the unused
profile never trigger a re-run.

In CI the store is carried across runs with `actions/cache`, so a push only
re-renders the cases whose inputs actually changed. Escape hatches:

```bash
GALLERY_NO_CACHE=1      bash infra/build_case.sh <case> ci   # ignore the cache
GALLERY_CACHE_REFRESH=1 bash infra/build_case.sh <case> ci   # rebuild + repopulate
GALLERY_CACHE_DIR=/path bash infra/build_case.sh <case> ci   # relocate the store
```

## What CI checks

On a pull request (`validate` + `build` workflows):

1. `python infra/validate.py` - schema + required files for every case.
2. Build, run and render the `ci` profile of the **affected** cases only - those
   whose files changed, or every case when a shared input changes (the figure
   engine/scripts or `environment.yml`). The per-ref samurai builds and the
   rendered-media store are restored read-only, so unaffected work is reused and
   the check fails if an affected case breaks. A doc-only PR builds nothing.

On a push to `main` (`deploy` workflow): the same build over all cases (cached),
then the Astro site is built and deployed to GitHub Pages.
