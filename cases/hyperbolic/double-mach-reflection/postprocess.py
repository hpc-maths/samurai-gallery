#!/usr/bin/env python
"""Generate the media for the double-mach-reflection case (density field)."""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="double_mach_reflection_hllc",
        field="rho",
        cmap="inferno",
        show_grid=True,
        thumb_frac=1.0,  # the double Mach structure is fully formed at the end
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
