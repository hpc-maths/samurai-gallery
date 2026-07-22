# Sod shock tube

The Sod problem is *the* reference test for compressible solvers: a membrane
separating a high-pressure gas from a low-pressure gas is removed, and the
solution develops the three characteristic waves - a rarefaction fan, a contact
discontinuity, and a shock. Here it is set up along the diagonal of a 2D domain.

Powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
engine.

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$), with the classic Sod
initial states $(\rho, u, p) = (1, 0, 1)$ on one side and $(0.125, 0, 0.1)$ on
the other.

## Numerical method

- **Flux:** HLLC. **Time:** explicit Euler.
- **Adaptation:** multiresolution.

The image shows the density $\rho$.

## What to look for

Three well-separated waves. The mesh refines on the shock and the contact
discontinuity (both sharp) while the smooth rarefaction fan needs fewer cells.
