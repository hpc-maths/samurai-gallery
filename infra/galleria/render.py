"""Render a samurai output series to theme-aware media.

Each case produces two variants so the gallery looks right in both themes:
  - dark:  dark canvas, bright-on-dark colormap, light mesh overlay
  - light: light canvas, light-low colormap, dark mesh overlay
Files are written next to the case as thumbnail-<theme>.png / preview-<theme>.mp4.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

from .h5 import list_frames, read_frame_1d, read_frame_2d

# Target preview length in seconds. The frame rate is derived per case from
# this so that all animations run for the same time at a comfortable pace,
# regardless of how many frames each simulation produced.
DEFAULT_DURATION = 12.0
_MIN_FPS = 2.0
_MAX_FPS = 30.0

# Per-theme canvas/overlay colors.
STYLES = {
    "dark": {
        "bg": "#0b0f17",
        "grid": "#ffffff",
        "line": "#ff7a45",
        "marker": "#4cc9f0",
        "spine": "#2a3446",
        "tick": "#6b7891",
        "gridline": "#1a2333",
    },
    "light": {
        "bg": "#f6f8fb",
        "grid": "#2b3648",
        "line": "#e15828",
        "marker": "#1391c4",
        "spine": "#c3ccd8",
        "tick": "#8b95a6",
        "gridline": "#e0e6ef",
    },
}

# Light-theme replacement for dark-optimized colormaps: keep the same hue
# family but with a light (near-white) low end so empty regions blend into the
# light page. Diverging maps (white center) already work on both themes.
LIGHT_CMAP = {
    "magma": "YlOrRd",
    "inferno": "YlOrRd",
    "plasma": "YlOrRd",
    "viridis": "YlGnBu",
    "cividis": "YlGnBu",
    "RdBu": "RdBu",
    "RdBu_r": "RdBu_r",
    "coolwarm": "coolwarm",
}


def _fps_for(n_frames: int, duration: float, override):
    if override:
        return override
    if duration <= 0 or n_frames <= 1:
        return _MIN_FPS
    return min(_MAX_FPS, max(_MIN_FPS, n_frames / duration))


def _writer(fps):
    # yuv420p + faststart make the mp4 stream and autoplay reliably in browsers.
    return matplotlib.animation.FFMpegWriter(
        fps=fps,
        bitrate=3200,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )


def _compute_range(files, field, component=None, symmetric=False):
    lo, hi = np.inf, -np.inf
    for path in files:
        _, values = read_frame_2d(path, field, component)
        lo = min(lo, float(values.min()))
        hi = max(hi, float(values.max()))
    if symmetric:
        m = max(abs(lo), abs(hi))
        lo, hi = -m, m
    if hi - lo < 1e-12:
        hi = lo + 1e-12
    return lo, hi


def _make_collection(polys, values, vmin, vmax, cmap, show_grid, grid_color):
    coll = PolyCollection(
        polys,
        array=values,
        cmap=cmap,
        edgecolors=grid_color if show_grid else "none",
        linewidths=0.15 if show_grid else 0.0,
    )
    coll.set_clim(vmin, vmax)
    return coll


def _render_2d_variant(
    files, field, component, vmin, vmax, extent, cmap, show_grid, style, thumb_index, fps, dpi, thumb_out, video_out
):
    bg = style["bg"]
    xmin, ymin, xmax, ymax = extent
    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    writer = _writer(fps)
    with writer.saving(fig, video_out, dpi=dpi):
        for i, path in enumerate(files):
            polys, values = read_frame_2d(path, field, component)
            coll = _make_collection(polys, values, vmin, vmax, cmap, show_grid, style["grid"])
            artist = ax.add_collection(coll)
            writer.grab_frame(facecolor=bg)
            if i == thumb_index:
                fig.savefig(thumb_out, facecolor=bg)
            artist.remove()
    plt.close(fig)


def render_series_2d(
    directory: str,
    prefix: str,
    field: str = "u",
    *,
    component=None,
    symmetric: bool = False,
    thumb_frac: float = 0.5,
    cmap: str = "magma",
    cmap_light: str | None = None,
    show_grid: bool = True,
    duration: float = DEFAULT_DURATION,
    fps: float | None = None,
    dpi: int = 130,
):
    """Render a 2D series to dark and light media variants.

    Writes thumbnail-dark.png, thumbnail-light.png, preview-dark.mp4 and
    preview-light.mp4 in the current directory.

    ``symmetric`` clamps the color scale to [-M, M] (for signed fields such as a
    level set). ``thumb_frac`` selects the thumbnail frame (0 first, 1 last).
    ``duration`` is the target video length; the frame rate is derived from it.
    ``cmap`` is the dark-theme colormap; the light-theme one defaults to a
    light-low equivalent (see LIGHT_CMAP), overridable via ``cmap_light``.
    """
    files = list_frames(directory, prefix)
    fps = _fps_for(len(files), duration, fps)
    vmin, vmax = _compute_range(files, field, component, symmetric)

    polys0, _ = read_frame_2d(files[0], field, component)
    xmin, ymin = polys0.reshape(-1, 2).min(axis=0)
    xmax, ymax = polys0.reshape(-1, 2).max(axis=0)
    extent = (xmin, ymin, xmax, ymax)
    thumb_index = min(len(files) - 1, max(0, round((len(files) - 1) * thumb_frac)))

    light_cmap = cmap_light or LIGHT_CMAP.get(cmap, cmap)
    for theme, style in STYLES.items():
        _render_2d_variant(
            files, field, component, vmin, vmax, extent,
            cmap if theme == "dark" else light_cmap,
            show_grid, style, thumb_index, fps, dpi,
            f"thumbnail-{theme}.png", f"preview-{theme}.mp4",
        )


def _render_1d_variant(files, field, extent, show_cells, style, thumb_index, fps, dpi, thumb_out, video_out):
    bg = style["bg"]
    xmin, xmax, ymin, ymax = extent
    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    for spine in ax.spines.values():
        spine.set_color(style["spine"])
    ax.tick_params(colors=style["tick"], labelsize=8)
    ax.grid(True, color=style["gridline"], linewidth=0.6)
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.1, top=0.96)

    writer = _writer(fps)
    with writer.saving(fig, video_out, dpi=dpi):
        for i, path in enumerate(files):
            x, values = read_frame_1d(path, field)
            (line,) = ax.plot(x, values, color=style["line"], linewidth=2.0)
            artists = [line]
            if show_cells:
                artists.append(ax.scatter(x, values, s=6, color=style["marker"], alpha=0.8, zorder=3))
            writer.grab_frame(facecolor=bg)
            if i == thumb_index:
                fig.savefig(thumb_out, facecolor=bg)
            for a in artists:
                a.remove()
    plt.close(fig)


def render_series_1d(
    directory: str,
    prefix: str,
    field: str = "u",
    *,
    show_cells: bool = True,
    duration: float = DEFAULT_DURATION,
    fps: float | None = None,
    dpi: int = 130,
):
    """Render a 1D series to dark and light animated line-plot variants."""
    files = list_frames(directory, prefix)
    fps = _fps_for(len(files), duration, fps)

    xmin, xmax = np.inf, -np.inf
    ymin, ymax = np.inf, -np.inf
    for path in files:
        x, values = read_frame_1d(path, field)
        xmin, xmax = min(xmin, x.min()), max(xmax, x.max())
        ymin, ymax = min(ymin, values.min()), max(ymax, values.max())
    pad = 0.08 * (ymax - ymin if ymax > ymin else 1.0)
    extent = (xmin, xmax, ymin - pad, ymax + pad)
    thumb_index = len(files) // 2

    for theme, style in STYLES.items():
        _render_1d_variant(
            files, field, extent, show_cells, style, thumb_index, fps, dpi,
            f"thumbnail-{theme}.png", f"preview-{theme}.mp4",
        )
