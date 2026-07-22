# Isentropic vortex

A smooth vortex is superimposed on a uniform flow and advected across the
domain. Because the exact solution is simply the initial vortex translated, this
case is the standard benchmark for measuring the **order of accuracy** of a
compressible solver on smooth flows - the counterpart to the shock-dominated
tests.

Powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
engine.

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$). The initial condition adds
an isentropic perturbation to a uniform background so that entropy is constant
and the vortex is an exact travelling solution.

## Numerical method

- **Flux:** HLLC. **Time:** explicit Euler.
- **Adaptation:** multiresolution.

The image shows the density $\rho$.

## What to look for

The vortex keeps its shape as it moves - any distortion is numerical error. The
mesh refines on the vortex core, where the gradients are, and coarsens in the
uniform far field.
