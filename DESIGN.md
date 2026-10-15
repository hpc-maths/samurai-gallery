---
name: samurai gallery
description: A wall of adaptive-mesh simulations built with samurai.
colors:
  signal: "#a23c26"
  signal-graphite: "#f07f61"
  on-signal: "#f4f5f7"
  on-signal-graphite: "#0b0c0e"
  room: "#e6e8eb"
  room-graphite: "#0b0c0e"
  bezel: "#d3d7dc"
  bezel-graphite: "#16181c"
  bezel-hi: "#c3c8cf"
  bezel-hi-graphite: "#23262c"
  control-edge: "#6f7680"
  control-edge-graphite: "#626a74"
  screen-off: "#dde0e4"
  screen-off-graphite: "#101215"
  ink: "#121418"
  ink-graphite: "#e8eaed"
  ink-2: "#474e58"
  ink-2-graphite: "#a3aab3"
  etch: "#4b525c"
  etch-graphite: "#8a929c"
  code-bg: "#f3f4f6"
  code-bg-graphite: "#111316"
  solid-region: "#3b3e44"
typography:
  display:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(2.5rem, 6.4vw, 5.6rem)"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "-0.012em"
    fontVariation: "'wdth' 68"
  headline:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(2.2rem, 5vw, 4.4rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.01em"
    fontVariation: "'wdth' 70"
  title:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    fontVariation: "'wdth' 80"
  screen-title:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "0.98rem"
    fontWeight: 650
    lineHeight: 1.15
    fontVariation: "'wdth' 85"
  body:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  prose:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "1.04rem"
    fontWeight: 400
    lineHeight: 1.7
  control:
    fontFamily: "Archivo Variable, Archivo, Arial Narrow, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 500
  label:
    fontFamily: "Martian Mono, ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "0.66rem"
    fontWeight: 400
    letterSpacing: "0.04em"
    fontFeature: "'tnum'"
rounded:
  none: "0px"
spacing:
  bezel: "6px"
  room: "clamp(12px, 2.4vw, 28px)"
  control-height: "36px"
  max-width: "1680px"
components:
  screen:
    backgroundColor: "{colors.bezel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
  screen-glass-off:
    backgroundColor: "{colors.screen-off}"
  facet-button:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.none}"
    height: "{spacing.control-height}"
    padding: "0 10px"
  run-button-pressed:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.on-signal}"
    rounded: "{rounded.none}"
    size: "{spacing.control-height}"
  search-input:
    backgroundColor: "{colors.room}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    height: "{spacing.control-height}"
    padding: "0 10px 0 32px"
  filter-chip:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    height: "26px"
    padding: "0 6px 0 9px"
  filter-chip-hover:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.on-signal}"
  top-bezel:
    backgroundColor: "{colors.bezel}"
    textColor: "{colors.ink-2}"
    height: "52px"
  console:
    backgroundColor: "{colors.bezel}"
    textColor: "{colors.ink}"
---

# Design System: samurai gallery

## Overview

**Creative North Star: "The Visualization Wall"**

The site is the screen wall of a computing centre. Each simulation is a screen; the interface is the hardware around it: bezels, a console, small data etched under every screen. The site owns no color. All chroma comes from the figures, and one interface color marks what is active.

Two rooms carry the same wall. The graphite room (dark) is the default unless the visitor's OS asks for light; the daylight room (light grey) is its twin. Both are cool, near-neutral greys with a faint blue cast (hue about 255 to 265 in OKLCH, chroma under 0.02). The structure is tight and dense: a 6px bezel separates every screen, there are no radii, no shadows and no cards, and type is either condensed Archivo (the voice) or Martian Mono (the data).

Figures are part of the world, not decoration on top of it. The field and its adaptive mesh are always shown together, with the mesh drawn as joints between cells (see Components: Media layer).

**Key Characteristics:**
- Screens carry the color; the room, bezels and type stay neutral.
- One signal color, used only for active state, focus, selection and the pressed run button.
- Square everything (0px radius), flat everything, 6px bezels as the only structure.
- Condensed uppercase Archivo for headings; Martian Mono for every measured value.
- Same figure in both themes: the field never changes color with the room.

## Colors

A cool neutral room with a single coral signal; every other hue on the page belongs to a simulation.

### Primary
- **Lipari Coral** (`signal` daylight, `signal-graphite` graphite): the only interface color. Focus rings, selected facets and their counts, the pressed run button, filter chips, link hover, text selection, checkbox and range accents. Taken from the warm end of the lipari colormap so it belongs to the figures rather than competing with them. Text on a coral fill uses `on-signal` / `on-signal-graphite`.

### Neutral
- **Room** (`room`, `room-graphite`): page ground; also the ground of inputs and dropdown panels.
- **Bezel** (`bezel`, `bezel-graphite`): the structure. Top and bottom bezels, the console, the wall's gutters, plates under screens, the monitor frame on the case page.
- **Bezel Highlight** (`bezel-hi`, `bezel-hi-graphite`): 1px hairlines: bezel edges, spec-sheet rules, table rules.
- **Control Edge** (`control-edge`, `control-edge-graphite`): the 1px border of inputs and buttons, at 3:1 against the bezel and the room so controls stay identifiable.
- **Screen Off** (`screen-off`, `screen-off-graphite`): the glass of a screen before media loads, and empty-state panels.
- **Ink** (`ink`, `ink-graphite`): titles and body text.
- **Ink 2** (`ink-2`, `ink-2-graphite`): supporting sentences, inactive nav, standby titles.
- **Etch** (`etch`, `etch-graphite`): mono data labels, counts, placeholders, icons at rest. Holds at least 5.4:1 on bezel in both rooms.
- **Code Ground** (`code-bg`, `code-bg-graphite`): source listings only.
- **Solid Region** (`solid-region`): media only; obstacles and holes in a domain, a neutral that reads as solid in both rooms.

### Named Rules
**The No House Color Rule.** The site has no brand hue. If a surface needs color, it needs a figure, not a fill.

**The Signal Means Active Rule.** Lipari coral appears only where something is selected, focused, pressed or hovered for action. Never as decoration, never as a heading color, never as a background at rest.

**The Two Rooms Rule.** Every neutral exists as a daylight and a graphite pair under the same name; a new surface uses the token, never a raw grey.

## Typography

**Display Font:** Archivo Variable (with Archivo, Arial Narrow), width axis loaded
**Label/Mono Font:** Martian Mono (with ui-monospace, SF Mono, Menlo), weights 400 and 500

**Character:** Archivo, narrowed with the width axis, is the voice of the wall: tall, tight, industrial. Martian Mono is the etching: every number, unit, count and field symbol a machine would print.

### Hierarchy
- **Display** (800, width 68%, clamp(2.5rem, 6.4vw, 5.6rem), line-height 0.9, uppercase): the one thesis line on the wall page.
- **Headline** (800, width 70%, clamp(2.2rem, 5vw, 4.4rem), line-height 0.92, uppercase): a case title on its own screen.
- **Title** (700, width 80%, 1.15rem, uppercase): section heads on bezel bands (Case sheet, Source). Prose h2 runs larger (750, width 80%, 1.55rem, sentence case).
- **Screen Title** (650, width 85%, 0.98rem, line-height 1.15; 1.25rem on big screens): the case name on a plate, clamped to two lines.
- **Body** (400, 1rem, line-height 1.55): interface text. Long-form README prose runs at 1.04rem, line-height 1.7, max 72ch.
- **Control** (500, 0.82rem): facet buttons, chips, console buttons.
- **Label** (Martian Mono 400, 0.66rem, letter-spacing 0.04em, tabular figures): the etch. Field symbol, dimension, mesh levels, cell counts, t/T readout, spec-sheet keys. Uppercase with 0.1 to 0.12em tracking only for status words (Standby, No signal).

### Named Rules
**The Etched Data Rule.** Any measured or machine value (counts, levels, cells, ranges, file names, t/T) is set in Martian Mono with tabular figures. Prose words stay in Archivo.

**The Condensed Voice Rule.** Headings narrow, never widen: width 68 to 85% for display and titles; full width only for running text.

## Layout

The wall is a dense CSS grid inside a room container (max 1680px, side margin clamp(12px, 2.4vw, 28px), safe-area aware). Columns step with the viewport: 8 by default, 6 under 1280px, 4 under 1080px, 3 under 900px, 2 under 600px. Auto-flow is dense. The grid's gap and padding are both the 6px bezel, painted with the bezel color, so screens look set into one frame.

Screen sizes come from data, not position: a featured case spans 2x2 (2x1 under 600px), a domain with aspect ratio 1.8 or wider spans the full row, everything else is 1x1. Glass keeps the media's own aspect ratio.

The console is sticky under the top bezel on wide screens and becomes static under 720px. Two-column layouts (thesis line, case head, case body with a sticky spec sheet at 22rem) collapse to one column between 760 and 900px. The case monitor is centred and sized so its glass never exceeds min(78vh, 980px) tall.

**The Bezel Gutter Rule.** Gutters between screens, around the wall, around the monitor, around the neighbour links and as the dropdown frame are all the same 6px, in the bezel color. Do not introduce a second gutter size for screen-to-screen spacing.

## Elevation & Depth

Flat. No box shadows anywhere. Depth reads as tone and framing: the room is the ground, bezels sit one step off it, hairlines in bezel highlight mark edges, and glass is its own tone. A floating layer (facet dropdown) is distinguished by a 1px bezel-highlight border plus a 6px bezel-colored outline, the same frame a screen gets, not by a shadow.

**The Flat Wall Rule.** Lift is expressed by a bezel frame, never by a shadow or blur.

## Shapes

Every corner is square (0px). Edges are 1px hairlines or 6px bezels. The only non-solid line is the dashed bezel-highlight border of a standby screen, which marks an empty slot on the wall. The only gradient on the site is the field legend, built from the media's own colormap stops.

**The Square Corner Rule.** Radius is 0px for every surface and control the site draws.

## Components

### Screen (signature)
The unit of the wall. A link containing glass (media at its own aspect ratio over `screen-off`) and a plate underneath on the bezel: screen title, then one etched line (field symbol, dimension, equation, mesh levels, cell count) joined by middle dots and truncated with an ellipsis.
- **Hover:** title underlines (1px, offset 3px); while the wall clock is idle the preview video fades in (opacity, 0.25s, ease-out-expo curve) and plays from the start. Disabled under reduced motion.
- **Focus:** 2px signal outline drawn inside the screen (offset -2px).
- **Big / Wide:** see Layout. Wide screens letterbox (contain) rather than crop.
- **No signal:** missing media shows the etch "No signal: media not rendered yet", uppercase, centred on the glass.

### Standby Screen
A screen for a roadmap method with no case yet. Transparent glass with a 1px dashed bezel-highlight border and the etch "Standby"; the plate names the method in ink 2 with "On the samurai roadmap". Absence is shown, not hidden.

### Console
The control strip on a bezel band with hairlines top and bottom: search field, facet menus, transport (run/pause and the t/T scrubber), visible-screen count right-aligned, and a row of active chips when filters apply.
- **Search field:** 36px tall, room ground, 1px control-edge border, Martian Mono 0.78rem, search icon in etch. Focus turns the border signal.
- **Facet button:** 36px, transparent, 1px control-edge border, Archivo 500 0.82rem, chevron that rotates 180 degrees when open. Hover darkens the border to etch. Active: signal border and the selected count in signal (a number, so state is not carried by hue alone).
- **Facet panel:** room ground, bezel frame (see Elevation), options with a mono count on the right; facets with more than 10 values get a filter field. Roadmap methods appear as inert options tagged "roadmap".
- **Run button:** 36px square icon button. Pressed state fills signal with on-signal icon and swaps play for pause.
- **Scrubber:** native range with signal accent and an etched t/T readout; one clock drives every visible screen, keyboard operable as a native range.
- **Chip:** 26px, 1px signal border, mono facet key then value then a close icon. Hover fills signal.

### Navigation
Top bezel, 52px: lowercase "samurai" wordmark (Archivo 800, width 75%, 1.45rem) with an etched "gallery" beside it; links right in ink 2, ink on hover or current page; external links carry a small arrow icon and hide under 560px. The theme toggle is a 32px square with a 1px control-edge border and inline SVG sun/moon. The bottom bezel mirrors it with ink-2 text.

### Monitor (case page)
One screen alone: media in glass inside a 6px bezel frame, then a bar with the legend (field symbol in Archivo 600, a 10px gradient bar from media.json stops with a hairline border, etched min and max) and etched stats (mesh levels, cells, frames).

### Case Sheet
A definition list under a 1px top rule; each row is an etched key (7.5rem column) and a value, separated by bezel-highlight hairlines. Sticky beside the prose on wide screens. Reference links hover to signal.

### Source
A bezel band header (uppercase title, etched file name and line count) over the listing, which sits in code ground inside a 6px bezel frame with Martian Mono 0.74rem, line-height 1.7. Syntax colors come from the highlighter's light/dark pair.

### Media layer (figures)
Rendered in CI by the galleria renderer; the site only frames it.
- **Colormaps:** lipari for sequential fields, with its darkest 10% cut off so no cell goes near-black; vik for diverging fields with a symmetric range. Color range is the 0.2 to 99.8 percentile of values pooled across all frames.
- **Mesh as joints:** each cell is outlined in its own color shifted 26 units of CIELAB lightness (lighter on dark cells, darker on light ones, chroma reduced 15%). Joint width is 7% of the cell width, capped at 2.2px; joints thinner than 0.6px fade into the cell color. Fine cells get fine joints, coarse cells thick ones, so every refinement level reads without a grey overlay.
- **One figure, two rooms:** 2D figures have no background of their own and take the domain's exact shape; the dark and light files are the same pixels. Regions with no cells use the solid-region neutral.
- **Legend sidecar:** each render writes media.json (11 colormap stops evenly spaced in value, range, mesh levels, cell count, frames) that the site uses for the legend and the etched stats.

## Do's and Don'ts

### Do:
- **Do** let the figures carry all the color; keep every interface surface on room, bezel, glass and ink tokens.
- **Do** reserve lipari coral for active, focused, selected and pressed state, and pair it with a non-hue mark (a count, a fill, an icon swap, an outline).
- **Do** separate screens with the 6px bezel and frame any floating layer the same way.
- **Do** set every measured value in Martian Mono with tabular figures, and keep it at 0.66rem or larger.
- **Do** show the field and its mesh together, with joints from the galleria renderer, in every figure.
- **Do** show what is missing: standby screens for roadmap methods, "No signal" glass for unrendered media.

### Don't:
- **Don't** round corners, add box shadows, or wrap content in cards.
- **Don't** use gradients outside the field legend.
- **Don't** recolor a figure per theme or put a figure on its own background.
- **Don't** draw the mesh as a uniform line overlay; it greys out the field.
- **Don't** introduce a second interface hue.
