"""Shared helpers for samurai-gallery post-processing scripts.

A case's ``postprocess.py`` imports from this package to turn the ``.h5`` files
written by samurai into a thumbnail and a preview animation, with a consistent
look across the whole gallery.
"""

from .h5 import read_frame_2d, list_frames
from .render import render_series_2d

__all__ = ["read_frame_2d", "list_frames", "render_series_2d"]
