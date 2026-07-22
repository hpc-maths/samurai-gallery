# 2D Riemann problem (configuration 12)

A third Schulz-Rinne two-dimensional Riemann configuration. As in the others,
four constant states fill the four quadrants of the unit square; configuration
12 combines contact discontinuities and shocks into a symmetric,
vortex-generating pattern.

Powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
engine; the code shown is the scenario (the four quadrant states).

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$), piecewise-constant initial
data on the four quadrants of $[0, 1]^2$ (configuration 12).

## Numerical method

- **Flux:** HLLC. **Time:** explicit Euler.
- **Adaptation:** multiresolution with positivity-preserving prediction.

The image shows the density $\rho$.

## What to look for

Two shocks and two contact discontinuities interact and roll the contacts into
symmetric vortices. The adaptive mesh concentrates on the shocks and the
roll-up regions.
