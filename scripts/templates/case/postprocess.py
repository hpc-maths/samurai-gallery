#!/usr/bin/env python
"""Generate the media for the __SLUG__ case."""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="__SLUG__",
        field="u",       # name of the field written by main.cpp
        cmap="magma",
        show_grid=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
