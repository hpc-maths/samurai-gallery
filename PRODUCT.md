# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary audience is institutional: people who judge the samurai project from
the outside (laboratories, research funders, conference audiences, potential
partners). They visit the gallery to get a sense of what samurai can do and how
mature the project is. They are not necessarily numerical-methods specialists.

Researchers and engineers who evaluate or use samurai are a secondary audience.
They come to find a case close to their own problem, read the equations and the
code, and reproduce the run.

## Product Purpose

The samurai gallery is a catalogue of simulation cases built with samurai, the
C++ library for adaptive mesh refinement and multiresolution with finite-volume
schemes (finite-difference and lattice Boltzmann are on the roadmap). Each case
is a self-contained folder that the CI builds, runs and renders into a thumbnail
and a preview video, then publishes as a static site.

Success: an institutional visitor leaves impressed by the quality and the range
of the simulations and of the project behind them.

## Positioning

What only samurai can show: the adaptive mesh follows the solution. Every figure
shows the field and the mesh that resolves it together, at every refinement
level. Every case is reproducible from one folder, with the exact samurai
version it was tested against.

## Operating Context

- Cases live in `cases/<category>/<slug>/`, described by `case.yaml` (schema in
  `infra/schema/case.schema.json`), explained in `README.md` (Markdown + LaTeX),
  with the displayed code (`main.cpp` or an engine scenario).
- Media are generated in CI, never committed, and deployed with the site to
  GitHub Pages.
- The catalogue will grow from 13 to roughly 50 to 200 cases, with more
  contributors. Facets available today: method, equation, dimension, adaptation,
  difficulty, free tags, required build features (MPI, PETSc...), engine.

## Capabilities and Constraints

- Static site built with Astro (`site/`), deployed on GitHub Pages.
- Visitors must be able to find a case quickly when there are many cases and
  many tags. A flat row of filter buttons does not scale.
- Light and dark themes.
- The figure system (colormaps, mesh rendering) is defined in
  `infra/galleria/render.py`: one colormap in both themes, the mesh drawn as a
  joint around every cell.

## Brand Commitments

None. No logo, no institutional logos, no required colors or fonts. The project
name is written "samurai" in lowercase.

## Evidence on Hand

- 14 cases (13 with local data): advection, Burgers 1D/2D, Euler (Sod, 2D
  Riemann configurations, double Mach reflection, Kelvin-Helmholtz, Sedov,
  isentropic vortex), level set, two-scale capillarity, convection with an
  obstacle.
- No testimonials, user counts, benchmarks or press to show. Do not invent any.
- Known issue: `linear-convection-obstacle` diverges numerically; its media are
  not representative until the case is fixed.

## Product Principles

1. The simulations are the show: every page leads with the figures.
2. Show the mechanism: the field and the adaptive mesh, together, everywhere.
3. Rigor is credibility: equations, code, samurai version and references are
   one step away from every figure.
4. Built to grow: finding a case among two hundred must stay as easy as among
   thirteen.
