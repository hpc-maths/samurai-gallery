#!/usr/bin/env python
"""Generate the media for the 2D Riemann problem case (density field)."""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="riemann2d_config3_hllc",
        field="rho",
        cmap="inferno",
        show_grid=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
