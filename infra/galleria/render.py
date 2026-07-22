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

from .h5 import list_frames, read_frame_2d

_BG = "#0b0f17"


def _compute_range(files, field):
    lo, hi = np.inf, -np.inf
    for path in files:
        _, values = read_frame_2d(path, field)
        lo = min(lo, float(values.min()))
        hi = max(hi, float(values.max()))
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
    thumbnail: str = "thumbnail.png",
    video: str = "preview.mp4",
    cmap: str = "magma",
    show_grid: bool = True,
    fps: int = 15,
    dpi: int = 130,
):
    """Render every frame of a series; write ``video`` and ``thumbnail``."""
    files = list_frames(directory, prefix)
    vmin, vmax = _compute_range(files, field)

    # Domain extent from the first frame.
    polys0, _ = read_frame_2d(files[0], field)
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
    thumb_index = len(files) // 2  # a representative mid-run frame

    with writer.saving(fig, video, dpi=dpi):
        for i, path in enumerate(files):
            polys, values = read_frame_2d(path, field)
            coll = _make_collection(polys, values, vmin, vmax, cmap, show_grid)
            artist = ax.add_collection(coll)
            writer.grab_frame(facecolor=_BG)
            if i == thumb_index:
                fig.savefig(thumbnail, facecolor=_BG, bbox_inches="tight", pad_inches=0)
            artist.remove()

    plt.close(fig)
    return thumbnail, video
