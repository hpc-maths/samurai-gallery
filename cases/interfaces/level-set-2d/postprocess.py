#!/usr/bin/env python
"""Generate the media for the level-set-2d case.

phi is a signed distance: phi < 0 inside the interface, phi > 0 outside.
The diverging colormap is centered on 0, so the zero level (the interface)
sits at its neutral middle. Each side of the interface uses its own range,
which keeps the thin inside region as readable as the outside.
"""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="level_set_2d",
        field="phi",
        diverging=True,
        show_grid=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
