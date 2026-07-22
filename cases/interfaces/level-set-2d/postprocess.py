#!/usr/bin/env python
"""Generate the media for the level-set-2d case.

phi is a signed distance: phi < 0 inside the interface, phi > 0 outside.
A symmetric diverging colormap puts the zero level (the interface) at the
center of the color scale.
"""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="level_set_2d",
        field="phi",
        symmetric=True,
        cmap="RdBu_r",
        show_grid=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
