# Kelvin-Helmholtz instability

When two fluid layers slide past each other, the shear interface is unstable:
any small ripple grows and rolls up into a train of vortices - the
Kelvin-Helmholtz billows seen in clouds, ocean currents and countless
astrophysical flows. It is a favorite showcase for adaptive solvers because the
action is confined to thin, evolving shear layers.

This case is a **new scenario contributed to**
[`samurai-euler`](https://github.com/hpc-maths/samurai-euler); the code shown is
its definition (initial shear profile and the seeded perturbation).

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$). The domain $[0,1]^2$ has a
central layer ($0.25 < y < 0.75$) with density $\rho = 2$ moving right, and
outer layers with $\rho = 1$ moving left, at uniform pressure. A small vertical
velocity localized at each interface seeds the instability.

## Numerical method

- **Flux:** HLLC approximate Riemann solver.
- **Time:** explicit Euler.
- **Adaptation:** multiresolution with a positivity-preserving prediction.

The image shows the density $\rho$.

## What to look for

Two rows of billows form along the interfaces and roll the light and heavy
fluids into interlocking spirals. The adaptive mesh refines precisely along the
braided shear layers, leaving the uniform interiors coarse.
