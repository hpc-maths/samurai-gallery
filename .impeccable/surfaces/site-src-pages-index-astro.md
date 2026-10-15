---
version: 1
slug: "site-src-pages-index-astro"
primary_target: "site/src/pages/index.astro"
related_targets: ["site/src/pages/cases/[...id].astro","site/src/layouts/Base.astro"]
---

# Surface brief: gallery wall (index) and case screen

Scope: site/src/pages/index.astro (the wall), site/src/pages/cases/[...id].astro (one case as a single-screen wall), shared Base layout.
Mode: Experience. The simulations lead from the first viewport; the interface recedes.
Audience: institutional visitors (labs, funders, partners) first; researchers second.
Success: the visitor leaves impressed by the range and quality of the simulations; any case is findable among ~200.
Constraints: Astro static site on GitHub Pages; light and dark themes; no logos, no invented claims; figures are fixed by infra/galleria (lipari, mesh joints).

## Direction contract

THESIS: The gallery is the visualization wall of a computing centre: every simulation is a screen, the bezels are the only structure, and the site has no color of its own. It refuses the category default of a hero banner over a row of identical rounded cards, and the editorial cream-and-serif catalogue the site had before.

OWN-WORLD: Graphite room (dark) or daylight room (light grey) as ground. Thin bezels in a slightly lighter tone separate screens; information is etched on the bezel band under each screen in Martian Mono (field, dimension, mesh levels, cells) with the case title in condensed Archivo. One interface color only, lipari coral, reserved for active state (pressed facet, focus, scrub head). No cards, no shadows, no radii, no gradients other than the field legend.

STORY: The visitor sees a wall of living simulations, understands from the mesh joints that samurai adapts its mesh to the physics, filters the wall from the console to a family of problems, opens one screen, and finds the equations, the code, the samurai version and the color legend one scroll away.

FIRST VIEWPORT: Top bezel: lowercase "samurai" wordmark left, links right. Under it a one-line thesis in large condensed uppercase with one sentence of support. Then the console (search field, facet menus with counts, time scrubber with run/pause, visible-screen count) sticky at the top, and immediately the wall: featured cases on 2x2 screens, wide domains spanning a row, all others 1x1. At least two rows of screens are visible at 1440x900.

FORM: Visualization wall (candidate 4 of 7, assigned by the roll). Raises kept from declined challengers: standby screens for roadmap methods with no case yet (absence informs), one control (the t/T scrubber) drives every visible screen with a keyboard equivalent, state shown by a mark and not only a hue. seed: none (unavailable)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
