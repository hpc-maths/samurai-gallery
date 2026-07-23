#!/usr/bin/env python
"""Generate the media for the two-scale-capillarity case.

alpha_l is the large-scale liquid volume fraction: 1 in the liquid column,
0 in the surrounding gas. A sequential colormap shows the column being sheared
by the air jet and shedding ligaments as it atomizes.
"""

import sys

from galleria import render_series_2d


def main(output_dir: str) -> None:
    render_series_2d(
        output_dir,
        prefix="liquid_column_HLLC_order2_mass_transfer",
        field="alpha_l",
        cmap="viridis",
        show_grid=True,
        thumb_frac=0.7,  # the atomizing spray is well developed past mid-run
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
