#!/usr/bin/env python
"""Generate the media for the burgers-1d case."""

import sys

from galleria import render_series_1d


def main(output_dir: str) -> None:
    render_series_1d(
        output_dir,
        prefix="burgers_1d",
        field="u",
        show_cells=True,
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
