# 2D Riemann problem (configuration 4)

Another of the Schulz-Rinne two-dimensional Riemann configurations. The unit
square is divided into four quadrants of constant state; when released, the
four one-dimensional interactions across the quadrant edges combine into a
genuinely two-dimensional wave pattern.

Powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
engine; the code shown is the scenario (the four quadrant states).

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$), piecewise-constant initial
data on the four quadrants of $[0, 1]^2$ (configuration 4).

## Numerical method

- **Flux:** HLLC. **Time:** explicit Euler.
- **Adaptation:** multiresolution with positivity-preserving prediction.

The image shows the density $\rho$.

## What to look for

Four shocks bound a central interaction zone. Compare the pattern with
configuration 3 (a different set of quadrant states gives a very different
structure). The mesh follows every shock and contact.
