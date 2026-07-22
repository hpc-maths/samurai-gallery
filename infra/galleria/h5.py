"""Read samurai HDF5 output (explicit mesh export)."""

from __future__ import annotations

import glob
import os

import h5py
import numpy as np


def list_frames(directory: str, prefix: str) -> list[str]:
    """Return the sorted list of ``.h5`` frame files for a given prefix.

    samurai writes one file per output step named ``<prefix>_<frame>.h5``.
    """
    pattern = os.path.join(directory, f"{prefix}_*.h5")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"no frames matching {pattern!r}")
    return files


def _mesh_group(f: h5py.File):
    """Return the mesh group, transparently handling MPI (per-rank) output."""
    mesh = f["mesh"]
    if "points" in mesh:
        return [mesh]
    # MPI output: one subgroup per rank
    return [mesh[rank] for rank in mesh.keys()]


def read_frame_2d(h5path: str, field: str):
    """Read a 2D frame.

    Returns ``(polygons, values)`` where ``polygons`` is an ``(Ncells, 4, 2)``
    array of quad vertices and ``values`` is the ``(Ncells,)`` cell field.
    """
    stem = h5path[:-3] if h5path.endswith(".h5") else h5path
    polys_all = []
    vals_all = []
    with h5py.File(stem + ".h5", "r") as f:
        for mesh in _mesh_group(f):
            points = mesh["points"][:]           # (Npoints, >=2)
            conn = mesh["connectivity"][:]       # (Ncells, 4) for quads
            fields = mesh["fields"]
            if field not in fields:
                available = ", ".join(fields.keys())
                raise KeyError(f"field {field!r} not found; available: {available}")
            values = np.asarray(fields[field][:]).reshape(-1)
            polys = points[conn][:, :, :2]       # (Ncells, 4, 2)
            polys_all.append(polys)
            vals_all.append(values)
    return np.concatenate(polys_all, axis=0), np.concatenate(vals_all, axis=0)
