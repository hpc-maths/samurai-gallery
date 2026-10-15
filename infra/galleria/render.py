"""Render a samurai output series to theme-aware media.

Every case writes thumbnail-<theme>.png and preview-<theme>.mp4 for the dark and
light themes of the site.

2D fields use one colormap in both themes, so a value has the same color
wherever the figure is shown. The figure takes the shape of the domain and has
no background of its own, so the dark and light files are identical: the field
is rendered once and written under both names.

The adaptive mesh is drawn as a joint around each cell rather than as a line
overlay: the joint width is a fixed fraction of the cell width, and its color is
the cell color shifted in lightness (lighter on dark cells, darker on light
ones). Fine cells get thin joints and coarse cells thick ones, so the mesh stays
readable at every refinement level without graying out the field.

1D series are line plots whose axes follow the theme.

Each render also writes media.json, which the site reads to draw the color
legend and the mesh statistics next to the media.
"""

from __future__ import annotations

import importlib
import json
import shutil

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import Colormap, ListedColormap, Normalize, TwoSlopeNorm

from .h5 import list_frames, read_frame_1d, read_frame_2d

# Importing cmcrameri registers the cmc.* colormaps with matplotlib.
importlib.import_module("cmcrameri.cm")

THEMES = ("dark", "light")

# Target preview length in seconds. The frame rate is derived per case from
# this so that all animations run for the same time at a comfortable pace,
# regardless of how many frames each simulation produced.
DEFAULT_DURATION = 12.0
_MIN_FPS = 2.0
_MAX_FPS = 30.0

# Pixel size of the longest side of the rendered media.
THUMB_PX = 1200
VIDEO_PX = 1080

# Gallery palette (Crameri scientific colour maps: perceptually uniform,
# colour-vision-deficiency friendly, readable in grayscale).
SEQUENTIAL_CMAP = "cmc.lipari"
DIVERGING_CMAP = "cmc.vik"
# The darkest end of lipari is raised so no cell is near-black: the mesh joint
# must stay visible on every cell.
_SEQUENTIAL_FLOOR = 0.10

# Mesh joint: width as a fraction of the cell width, capped in pixels, and the
# lightness shift (CIELAB L*) between a cell and its joint.
JOINT_FRACTION = 0.07
JOINT_MAX_PX = 2.2
JOINT_DELTA_L = 26.0
# Below this width (px) a joint is faded into the cell color instead of being
# drawn thinner, so sub-pixel joints do not turn into a uniform gray veil.
_JOINT_MIN_PX = 0.6

# Color of regions with no cells (obstacles, holes in the domain): a neutral
# that reads as "solid" on both site themes. The figure never shows it
# elsewhere, since it takes the exact shape of the domain.
SOLID_COLOR = "#3b3e44"

# Robust color range: percentiles of the values pooled over all frames, so a
# single spike does not flatten the rest of the field.
RANGE_PERCENTILES = (0.2, 99.8)
_RANGE_SAMPLE = 200_000

# Theme of the 1D line plots (matches the site background).
STYLES_1D = {
    "dark": {"bg": "#0b0c0e", "axis": "#8a929c", "rug": "#e8eaed"},
    "light": {"bg": "#e6e8eb", "axis": "#4b525c", "rug": "#121418"},
}


def _fps_for(n_frames: int, duration: float, override):
    if override:
        return override
    if duration <= 0 or n_frames <= 1:
        return _MIN_FPS
    return min(_MAX_FPS, max(_MIN_FPS, n_frames / duration))


def _writer(fps):
    # yuv420p + faststart make the mp4 stream and autoplay reliably in browsers.
    # A constant quality keeps the mesh joints sharp without a fixed bitrate.
    return matplotlib.animation.FFMpegWriter(
        fps=fps,
        codec="libx264",
        extra_args=["-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------

_D65 = np.array([0.95047, 1.0, 1.08883])
_RGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
_XYZ_TO_RGB = np.linalg.inv(_RGB_TO_XYZ)


def _srgb_to_lab(rgb):
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _RGB_TO_XYZ.T / _D65
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], axis=1)


def _lab_to_srgb(lab):
    fy = (lab[:, 0] + 16) / 116
    f = np.stack([fy + lab[:, 1] / 500, fy, fy - lab[:, 2] / 200], axis=1)
    xyz = np.where(f > 6 / 29, f**3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * _D65
    lin = np.clip(xyz @ _XYZ_TO_RGB.T, 0, 1)
    return np.clip(np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055), 0, 1)


def _resolve_cmap(cmap, diverging: bool) -> Colormap:
    if cmap is not None:
        return plt.get_cmap(cmap)
    if diverging:
        return plt.get_cmap(DIVERGING_CMAP)
    base = plt.get_cmap(SEQUENTIAL_CMAP)
    return ListedColormap(base(np.linspace(_SEQUENTIAL_FLOOR, 1.0, 256)), name="gallery-sequential")


def _joint_colors(face_rgb):
    """Joint color of each cell: its own color, lighter if dark, darker if light."""
    lab = _srgb_to_lab(face_rgb)
    lightness = lab[:, 0]
    lab[:, 0] = np.clip(lightness + np.where(lightness < 52, JOINT_DELTA_L, -JOINT_DELTA_L), 0, 100)
    lab[:, 1:] *= 0.85
    return _lab_to_srgb(lab)


def _norm(vmin, vmax, diverging):
    if diverging and vmin < 0 < vmax:
        return TwoSlopeNorm(0.0, vmin=vmin, vmax=vmax)
    return Normalize(vmin, vmax, clip=True)


def _compute_range(files, field, component=None, symmetric=False):
    """Robust (lo, hi) over the whole series."""
    rng = np.random.default_rng(0)
    per_frame = max(1, _RANGE_SAMPLE // len(files))
    samples = []
    for path in files:
        _, values = read_frame_2d(path, field, component)
        if values.size > per_frame:
            values = rng.choice(values, per_frame, replace=False)
        samples.append(values)
    pooled = np.concatenate(samples)
    lo, hi = (float(v) for v in np.percentile(pooled, RANGE_PERCENTILES))
    if symmetric:
        m = max(abs(lo), abs(hi))
        lo, hi = -m, m
    if hi - lo < 1e-12:
        hi = lo + 1e-12
    return lo, hi


# ---------------------------------------------------------------------------
# 2D
# ---------------------------------------------------------------------------


def _even(n: float) -> int:
    # yuv420p needs even frame dimensions.
    return max(2, int(round(n / 2)) * 2)


def _figure_for(extent, longest_px, dpi):
    xmin, ymin, xmax, ymax = extent
    width, height = xmax - xmin, ymax - ymin
    if width >= height:
        wpx, hpx = _even(longest_px), _even(longest_px * height / width)
    else:
        wpx, hpx = _even(longest_px * width / height), _even(longest_px)
    fig = plt.figure(figsize=(wpx / dpi, hpx / dpi), dpi=dpi)
    fig.patch.set_facecolor(SOLID_COLOR)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")
    return fig, ax, wpx / width


def _cell_collection(polys, values, cmap, norm, show_grid, px_per_unit, dpi):
    faces = cmap(norm(values))[:, :3]
    if not show_grid:
        return PolyCollection(polys, facecolors=faces, edgecolors=faces, linewidths=0.3 * 72 / dpi)
    cell_px = (polys[:, :, 0].max(axis=1) - polys[:, :, 0].min(axis=1)) * px_per_unit
    joint_px = np.clip(JOINT_FRACTION * cell_px, 0.0, JOINT_MAX_PX)
    visibility = np.clip(joint_px / _JOINT_MIN_PX, 0.0, 1.0)[:, None]
    joints = faces * (1 - visibility) + _joint_colors(faces) * visibility
    widths = np.maximum(joint_px, _JOINT_MIN_PX) * 72 / dpi
    return PolyCollection(polys, facecolors=faces, edgecolors=joints, linewidths=widths)


MEDIA_META = "media.json"
_LEGEND_STOPS = 11


def _mesh_stats(polys):
    """Number of distinct cell sizes (refinement levels) and of cells in a frame."""
    widths = polys[:, :, 0].max(axis=1) - polys[:, :, 0].min(axis=1)
    levels = np.unique(np.round(np.log2(widths.max() / widths)).astype(int))
    return {"levels": int(levels.size), "cells": int(widths.size)}


def _write_meta(meta):
    with open(MEDIA_META, "w") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")


def _legend(cmap, norm, vmin, vmax):
    """Colormap stops evenly spaced in value, as hex, for the site legend."""
    values = np.linspace(vmin, vmax, _LEGEND_STOPS)
    return [matplotlib.colors.to_hex(c) for c in cmap(norm(values))]


def render_series_2d(
    directory: str,
    prefix: str,
    field: str = "u",
    *,
    component=None,
    symmetric: bool = False,
    diverging: bool | None = None,
    vrange: tuple[float, float] | None = None,
    thumb_frac: float = 0.5,
    cmap: str | None = None,
    show_grid: bool = True,
    duration: float = DEFAULT_DURATION,
    fps: float | None = None,
):
    """Render a 2D series to thumbnail-<theme>.png and preview-<theme>.mp4.

    ``symmetric`` clamps the color scale to [-M, M]. Signed fields (``symmetric``
    or ``diverging=True``) use the diverging gallery colormap centered on 0;
    other fields use the sequential one. ``vrange`` fixes the color range
    instead of the robust range computed from the series. ``cmap`` overrides the
    gallery colormap and should stay exceptional. ``thumb_frac`` selects the
    thumbnail frame (0 first, 1 last). ``duration`` is the target video length;
    the frame rate is derived from it.
    """
    files = list_frames(directory, prefix)
    fps = _fps_for(len(files), duration, fps)
    diverging = symmetric if diverging is None else diverging
    vmin, vmax = vrange if vrange else _compute_range(files, field, component, symmetric)
    colormap = _resolve_cmap(cmap, diverging)
    norm = _norm(vmin, vmax, diverging)

    polys0, _ = read_frame_2d(files[0], field, component)
    xmin, ymin = polys0.reshape(-1, 2).min(axis=0)
    xmax, ymax = polys0.reshape(-1, 2).max(axis=0)
    extent = (xmin, ymin, xmax, ymax)
    thumb_index = min(len(files) - 1, max(0, round((len(files) - 1) * thumb_frac)))

    dpi = 100
    for out, longest in (("thumbnail", THUMB_PX), ("preview", VIDEO_PX)):
        fig, ax, px_per_unit = _figure_for(extent, longest, dpi)
        if out == "thumbnail":
            polys, values = read_frame_2d(files[thumb_index], field, component)
            ax.add_collection(_cell_collection(polys, values, colormap, norm, show_grid, px_per_unit, dpi))
            fig.savefig("thumbnail-dark.png", dpi=dpi)
            _write_meta(
                {
                    "dimension": 2,
                    "field": field,
                    "range": [vmin, vmax],
                    "diverging": bool(diverging),
                    "legend": _legend(colormap, norm, vmin, vmax),
                    "aspect": float((xmax - xmin) / (ymax - ymin)),
                    "frames": len(files),
                    "mesh": _mesh_stats(polys),
                }
            )
        else:
            writer = _writer(fps)
            with writer.saving(fig, "preview-dark.mp4", dpi=dpi):
                for path in files:
                    polys, values = read_frame_2d(path, field, component)
                    artist = ax.add_collection(
                        _cell_collection(polys, values, colormap, norm, show_grid, px_per_unit, dpi)
                    )
                    writer.grab_frame()
                    artist.remove()
        plt.close(fig)

    shutil.copyfile("thumbnail-dark.png", "thumbnail-light.png")
    shutil.copyfile("preview-dark.mp4", "preview-light.mp4")


# ---------------------------------------------------------------------------
# 1D
# ---------------------------------------------------------------------------


def _render_1d_variant(files, field, extent, show_cells, style, color, thumb_index, fps, thumb_out, video_out):
    bg = style["bg"]
    xmin, xmax, ymin, ymax = extent
    dpi = 200
    fig = plt.figure(figsize=(THUMB_PX / dpi, THUMB_PX / dpi), dpi=dpi)
    fig.patch.set_facecolor(bg)
    ax = fig.add_axes([0.1, 0.1, 0.86, 0.84])
    ax.set_facecolor(bg)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(style["axis"])
        ax.spines[side].set_linewidth(0.6)
    ax.tick_params(colors=style["axis"], labelsize=6, width=0.6, length=3)
    # One tick per cell along the bottom: the density of the rug shows the
    # adaptive mesh.
    rug_lo, rug_hi = ymin + 0.01 * (ymax - ymin), ymin + 0.045 * (ymax - ymin)

    video_dpi = dpi * VIDEO_PX / THUMB_PX
    writer = _writer(fps)
    with writer.saving(fig, video_out, dpi=video_dpi):
        for i, path in enumerate(files):
            x, values = read_frame_1d(path, field)
            artists = [
                ax.fill_between(x, values, ymin, color=color, alpha=0.12, linewidth=0),
                ax.plot(x, values, color=color, linewidth=1.4)[0],
            ]
            if show_cells:
                artists.append(ax.vlines(x, rug_lo, rug_hi, color=style["rug"], linewidth=0.3, alpha=0.6))
            writer.grab_frame(facecolor=bg)
            if i == thumb_index:
                fig.savefig(thumb_out, facecolor=bg, dpi=dpi)
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
    color = _resolve_cmap(None, diverging=False)(0.62)
    x, _ = read_frame_1d(files[thumb_index], field)
    spacing = np.diff(x)
    levels = np.unique(np.round(np.log2(spacing.max() / spacing)).astype(int))
    _write_meta(
        {
            "dimension": 1,
            "field": field,
            "range": [float(ymin), float(ymax)],
            "frames": len(files),
            "mesh": {"levels": int(levels.size), "cells": int(x.size)},
        }
    )

    for theme in THEMES:
        _render_1d_variant(
            files, field, extent, show_cells, STYLES_1D[theme], color, thumb_index, fps,
            f"thumbnail-{theme}.png", f"preview-{theme}.mp4",
        )
