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
# 1. Create the dedicated environment (toolchain + samurai deps + media stack)
micromamba create -f environment.yml
micromamba activate samurai-gallery

# 2. Build, run and render any case end to end
bash infra/build_case.sh cases/getting-started/advection-2d ci
```

This produces `thumbnail.png` and `preview.mp4` in the case directory. The
driver builds the samurai version pinned by the case (`samurai.ref` in its
`case.yaml`) into a per-ref cache under `~/.cache/samurai-gallery` and links the
case against it - no manual samurai install needed.

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

Each case pins the samurai version it is tested against in its `case.yaml`
(`samurai.ref` for finite-volume cases, `engine.repo`+`engine.ref` for
compressible-Euler cases). The deploy workflow builds each pinned version on
demand via `infra/build_case.sh` and caches the per-ref installs and engine
checkouts under `~/.cache/samurai-gallery` (persisted across runs by
`actions/cache`). To bump a case, change its ref in `case.yaml`.

**One-time setup:** in the repository settings, set **Pages → Source** to
**GitHub Actions**. Each Euler case's scenario must be present on the
`engine.ref` it declares in its `case.yaml`.
