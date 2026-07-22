# samurai gallery

A curated, auto-generated gallery of simulation cases built with
[samurai](https://github.com/hpc-maths/samurai), the adaptive-mesh (AMR /
multiresolution) library for finite-volume schemes (with finite-difference and
LBM support on the roadmap).

Each case is a self-contained folder. From that single source of truth the
project builds the simulation, runs it, renders a preview video and thumbnail,
and publishes a modern website (GitHub Pages) showing the explanation, the code
and the media.

## Repository layout

```
cases/<category>/<name>/   one self-contained case (see CONTRIBUTING.md)
infra/                     schema, build/run driver, shared post-processing lib
scripts/                   scaffolding (new-case.py) + case template
site/                      the Astro website (increment 2)
environment.yml            the dedicated conda/micromamba environment
```

## Quick start

```bash
# 1. Create the dedicated environment (installs the toolchain + samurai deps)
micromamba create -f environment.yml
micromamba activate samurai-gallery

# 2. Install samurai into the environment so find_package(samurai) works
cmake -S /path/to/samurai -B /tmp/samurai-build \
    -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" -DCMAKE_BUILD_TYPE=Release
cmake --install /tmp/samurai-build

# 3. Build, run and render any case end to end
bash infra/build_case.sh cases/getting-started/advection-2d ci
```

This produces `thumbnail.png` and `preview.mp4` in the case directory.

## Adding a case

See [CONTRIBUTING.md](CONTRIBUTING.md). In short:

```bash
python scripts/new-case.py --category getting-started --slug my-case \
    --title "My case" --equation linear-advection
# edit the generated files, then:
bash infra/build_case.sh cases/getting-started/my-case ci
```

## Status

- [x] Increment 1: repository foundations, case contract, build/run/render pipeline
- [x] Increment 2: Astro website (editorial "revue" design, light/dark, theme-aware media)
- [x] Increment 3: GitHub Actions CI/CD + Pages deploy
- [x] Increment 4: v1 case set (13 finite-volume / compressible-Euler cases)

## Deployment

Two GitHub Actions workflows (`.github/workflows/`):

- **validate** - on every push and pull request: schema + required-files check
  for all cases (fast, no compilation).
- **deploy** - on push to `main` (or manual dispatch): builds every case's media
  (compile → run → render), builds the Astro site, and deploys to GitHub Pages.
  Per-case failures are non-fatal - the site always deploys, with a placeholder
  for any case whose media is missing.

The deploy workflow builds samurai from source into the `samurai-gallery`
environment and, for the compressible-Euler cases, sets up the
[`samurai-euler`](https://github.com/hpc-maths/samurai-euler) engine env. Pin
the upstream refs via the `SAMURAI_REF` / `SAMURAI_EULER_REF` env vars at the
top of `deploy.yml`.

**One-time setup:** in the repository settings, set **Pages → Source** to
**GitHub Actions**. The Euler cases (Kelvin-Helmholtz, Sedov, Riemann, ...) need
their scenarios present on the `SAMURAI_EULER_REF` branch of samurai-euler.
