"""Read samurai HDF5 output (explicit mesh export)."""

from __future__ import annotations

import glob
import os
import re

import h5py
import numpy as np


def _frame_key(path: str):
    """Natural-sort key: order by the last integer in the file name.

    Handles both zero-padded gallery output (``prefix_0007``) and samurai's
    unpadded ``prefix_ite_7`` naming, and puts an ``_init`` snapshot first.
    """
    stem = os.path.basename(path)
    nums = re.findall(r"\d+", stem)
    return int(nums[-1]) if nums else -1


def list_frames(directory: str, prefix: str) -> list[str]:
    """Return the frame ``.h5`` files for a given prefix, in time order.

    samurai writes one file per output step, e.g. ``<prefix>_<frame>.h5``.
    """
    pattern = os.path.join(directory, f"{prefix}_*.h5")
    files = sorted(glob.glob(pattern), key=_frame_key)
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


def read_frame_1d(h5path: str, field: str):
    """Read a 1D frame.

    Returns ``(x, values)`` sorted by cell-center abscissa, where ``x`` is the
    array of cell centers and ``values`` the ``(Ncells,)`` cell field.
    """
    stem = h5path[:-3] if h5path.endswith(".h5") else h5path
    xs_all = []
    vals_all = []
    with h5py.File(stem + ".h5", "r") as f:
        for mesh in _mesh_group(f):
            points = mesh["points"][:]           # (Npoints, >=1)
            conn = mesh["connectivity"][:]       # (Ncells, 2) segments
            fields = mesh["fields"]
            values = _scalarize(_read_raw(fields, field), None)
            seg_x = points[conn][:, :, 0]         # (Ncells, 2)
            centers = seg_x.mean(axis=1)
            xs_all.append(centers)
            vals_all.append(values)
    x = np.concatenate(xs_all)
    v = np.concatenate(vals_all)
    order = np.argsort(x)
    return x[order], v[order]


def _read_raw(fields, field):
    """Read a field, transparently reassembling split vector components.

    samurai writes a vector field ``u`` as separate datasets ``u_0``, ``u_1``,
    ... This returns a ``(Ncells,)`` array for scalars or ``(Ncells, k)`` for
    vectors.
    """
    if field in fields:
        return np.asarray(fields[field][:])
    comps = []
    i = 0
    while f"{field}_{i}" in fields:
        comps.append(np.asarray(fields[f"{field}_{i}"][:]).reshape(-1))
        i += 1
    if comps:
        return np.stack(comps, axis=1)
    available = ", ".join(fields.keys())
    raise KeyError(f"field {field!r} not found; available: {available}")


def _scalarize(raw: np.ndarray, component):
    """Reduce a possibly multi-component field to one value per cell.

    ``component`` is an int (pick that component) or None (magnitude for vector
    fields, identity for scalars).
    """
    arr = np.asarray(raw)
    if arr.ndim == 1:
        return arr
    # (Ncells, k) multi-component field
    if component is not None:
        return arr[:, component]
    return np.sqrt(np.sum(arr * arr, axis=1))


def read_frame_2d(h5path: str, field: str, component=None):
    """Read a 2D frame.

    Returns ``(polygons, values)`` where ``polygons`` is an ``(Ncells, 4, 2)``
    array of quad vertices and ``values`` is the ``(Ncells,)`` cell field.
    Multi-component (vector) fields are reduced via ``component`` (index) or, if
    None, their magnitude.
    """
    stem = h5path[:-3] if h5path.endswith(".h5") else h5path
    polys_all = []
    vals_all = []
    with h5py.File(stem + ".h5", "r") as f:
        for mesh in _mesh_group(f):
            points = mesh["points"][:]           # (Npoints, >=2)
            conn = mesh["connectivity"][:]       # (Ncells, 4) for quads
            fields = mesh["fields"]
            values = _scalarize(_read_raw(fields, field), component)
            polys = points[conn][:, :, :2]       # (Ncells, 4, 2)
            polys_all.append(polys)
            vals_all.append(values)
    return np.concatenate(polys_all, axis=0), np.concatenate(vals_all, axis=0)
