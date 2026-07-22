#!/usr/bin/env python
"""Generate the media for the advection-2d case.

Usage: postprocess.py <output_dir>
The output dir contains the .h5 frames written by the simulation.
"""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="advection_2d",
        field="u",
        cmap="magma",
        show_grid=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
