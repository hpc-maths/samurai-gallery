# Sedov blast wave

A large amount of energy is deposited in a tiny region of an ambient gas at
rest. The result is a strong, self-similar **circular blast wave** that expands
outward - the classic Sedov-Taylor problem, a demanding test of a compressible
solver's shock capturing and symmetry preservation.

This case is powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
solver engine. The code shown here is the scenario definition (initial and
boundary conditions); the flux, time integration and adaptation are provided by
the shared engine.

## Equations

The compressible Euler equations for an ideal gas ($\gamma = 1.4$):

$$
\partial_t \rho + \nabla \cdot (\rho \mathbf{u}) = 0, \qquad
\partial_t (\rho \mathbf{u}) + \nabla \cdot (\rho \mathbf{u} \otimes \mathbf{u} + p\, I) = 0, \qquad
\partial_t (\rho E) + \nabla \cdot ((\rho E + p)\, \mathbf{u}) = 0.
$$

The initial state is an ambient gas ($\rho = 1$, $p = 10^{-5}$) with a small
disc of radius $0.1$ at the center holding a large pressure set from the blast
energy $E$.

## Numerical method

- **Flux:** HLLC approximate Riemann solver.
- **Time:** explicit Euler, $\Delta t = \text{CFL}\, \Delta x / \max(|u| + c)$.
- **Adaptation:** multiresolution with a positivity-preserving prediction
  operator, so density and pressure stay physical near the shock.

The image shows the density $\rho$.

## What to look for

A thin, high-density shell expands as a near-perfect circle. The multiresolution
mesh tracks the shell as it grows, keeping the interior and far field coarse.
