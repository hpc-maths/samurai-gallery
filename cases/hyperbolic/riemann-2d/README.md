# 2D Riemann problem (configuration 3)

The unit square is split into four quadrants, each holding a different constant
state of a compressible gas. When released, the four states interact through a
rich pattern of shocks, contact discontinuities and a rolled-up central jet -
one of the classic two-dimensional Riemann configurations (Schulz-Rinne). It is
a favorite stress test for high-resolution and adaptive schemes.

This case is powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
solver engine; the code shown here is the scenario (the four quadrant states and
boundary conditions).

## Equations

The compressible Euler equations for an ideal gas ($\gamma = 1.4$), with the
initial state piecewise constant on the four quadrants of $[0, 1]^2$ meeting at
$(0.5, 0.5)$.

## Numerical method

- **Flux:** HLLC approximate Riemann solver.
- **Time:** explicit Euler.
- **Adaptation:** multiresolution with a positivity-preserving prediction.

The image shows the density $\rho$.

## What to look for

Curved shocks bound the interaction region, and a thin, unstable jet develops
along the diagonal and rolls up. The adaptive mesh follows every discontinuity,
which is what makes the fine-scale roll-up affordable.
