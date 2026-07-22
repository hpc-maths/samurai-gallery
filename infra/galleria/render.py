"""Render a 2D samurai output series to a thumbnail and a preview video.

The look is intentionally uniform across the gallery: dark background, no axes,
optional light mesh overlay to showcase the adaptive grid.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

from .h5 import list_frames, read_frame_1d, read_frame_2d

_BG = "#0b0f17"
_ACCENT = "#ff7a45"
_ACCENT_2 = "#4cc9f0"

# Target preview length in seconds. The frame rate is derived per case from
# this so that all animations run for the same time at a comfortable pace,
# regardless of how many frames each simulation produced.
DEFAULT_DURATION = 8.0
_MIN_FPS = 4.0
_MAX_FPS = 30.0


def _fps_for(n_frames: int, duration: float, override):
    """Frame rate that plays ``n_frames`` over ``duration`` seconds."""
    if override:
        return override
    if duration <= 0 or n_frames <= 1:
        return _MIN_FPS
    return min(_MAX_FPS, max(_MIN_FPS, n_frames / duration))


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


def _make_collection(polys, values, vmin, vmax, cmap, show_grid):
    coll = PolyCollection(
        polys,
        array=values,
        cmap=cmap,
        edgecolors="white" if show_grid else "none",
        linewidths=0.15 if show_grid else 0.0,
    )
    coll.set_clim(vmin, vmax)
    return coll


def render_series_2d(
    directory: str,
    prefix: str,
    field: str = "u",
    *,
    component=None,
    symmetric: bool = False,
    thumb_frac: float = 0.5,
    thumbnail: str = "thumbnail.png",
    video: str = "preview.mp4",
    cmap: str = "magma",
    show_grid: bool = True,
    duration: float = DEFAULT_DURATION,
    fps: float | None = None,
    dpi: int = 130,
):
    """Render every frame of a series; write ``video`` and ``thumbnail``.

    ``symmetric`` clamps the color scale to [-M, M] (useful for signed fields
    such as a level set, so the zero level sits at the middle of the colormap).
    ``thumb_frac`` selects which frame becomes the thumbnail (0 = first,
    1 = last); use a late frame for cases whose structure develops over time.
    ``duration`` sets the target video length in seconds; the frame rate is
    derived from it so every case animates at the same pace regardless of how
    many frames it has (pass ``fps`` to override).
    """
    files = list_frames(directory, prefix)
    fps = _fps_for(len(files), duration, fps)
    vmin, vmax = _compute_range(files, field, component, symmetric)

    # Domain extent from the first frame.
    polys0, _ = read_frame_2d(files[0], field, component)
    xmin, ymin = polys0.reshape(-1, 2).min(axis=0)
    xmax, ymax = polys0.reshape(-1, 2).max(axis=0)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=dpi)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    # yuv420p + faststart make the mp4 stream and autoplay reliably in browsers.
    writer = matplotlib.animation.FFMpegWriter(
        fps=fps,
        bitrate=3200,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    thumb_index = min(len(files) - 1, max(0, round((len(files) - 1) * thumb_frac)))

    with writer.saving(fig, video, dpi=dpi):
        for i, path in enumerate(files):
            polys, values = read_frame_2d(path, field, component)
            coll = _make_collection(polys, values, vmin, vmax, cmap, show_grid)
            artist = ax.add_collection(coll)
            writer.grab_frame(facecolor=_BG)
            if i == thumb_index:
                fig.savefig(thumbnail, facecolor=_BG, bbox_inches="tight", pad_inches=0)
            artist.remove()

    plt.close(fig)
    return thumbnail, video


def render_series_1d(
    directory: str,
    prefix: str,
    field: str = "u",
    *,
    thumbnail: str = "thumbnail.png",
    video: str = "preview.mp4",
    color: str = _ACCENT,
    show_cells: bool = True,
    duration: float = DEFAULT_DURATION,
    fps: float | None = None,
    dpi: int = 130,
):
    """Render a 1D output series as an animated line plot.

    Cell centers are marked (``show_cells``) so the viewer sees where the
    adaptive mesh concentrates points. ``duration`` sets the target video
    length in seconds; the frame rate is derived from it (pass ``fps`` to
    override) so every case animates at the same pace.
    """
    files = list_frames(directory, prefix)
    fps = _fps_for(len(files), duration, fps)

    xmin, xmax = np.inf, -np.inf
    ymin, ymax = np.inf, -np.inf
    for path in files:
        x, values = read_frame_1d(path, field)
        xmin, xmax = min(xmin, x.min()), max(xmax, x.max())
        ymin, ymax = min(ymin, values.min()), max(ymax, values.max())
    pad = 0.08 * (ymax - ymin if ymax > ymin else 1.0)
    ymin, ymax = ymin - pad, ymax + pad

    fig, ax = plt.subplots(figsize=(7, 4.6), dpi=dpi)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    for spine in ax.spines.values():
        spine.set_color("#2a3446")
    ax.tick_params(colors="#6b7891", labelsize=8)
    ax.grid(True, color="#1a2333", linewidth=0.6)
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.1, top=0.96)

    writer = matplotlib.animation.FFMpegWriter(
        fps=fps,
        bitrate=3200,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    thumb_index = len(files) // 2

    with writer.saving(fig, video, dpi=dpi):
        for i, path in enumerate(files):
            x, values = read_frame_1d(path, field)
            (line,) = ax.plot(x, values, color=color, linewidth=2.0)
            artists = [line]
            if show_cells:
                artists.append(
                    ax.scatter(x, values, s=6, color=_ACCENT_2, alpha=0.7, zorder=3)
                )
            writer.grab_frame(facecolor=_BG)
            if i == thumb_index:
                fig.savefig(thumbnail, facecolor=_BG, bbox_inches="tight", pad_inches=0.1)
            for a in artists:
                a.remove()

    plt.close(fig)
    return thumbnail, video
