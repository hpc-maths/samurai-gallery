# Double Mach reflection

A strong (Mach 10) shock in air travels along a wall and strikes a $30^\circ$
ramp. The reflection is irregular: it produces two triple points, a curved
Mach stem and a jet of dense gas that sprays along the wall. This is one of the
most demanding classical benchmarks for adaptive compressible solvers.

Powered by the [`samurai-euler`](https://github.com/hpc-maths/samurai-euler)
engine; the code shown is the scenario (initial state and the time-dependent
imposed boundary conditions).

## Equations

Compressible Euler for an ideal gas ($\gamma = 1.4$). The incident shock enters
from the left; the post-shock state is imposed on the top boundary so the shock
moves at the correct speed.

## Numerical method

- **Flux:** HLLC. **Time:** explicit Euler.
- **Adaptation:** multiresolution with positivity-preserving prediction.

The image shows the density $\rho$.

## What to look for

The rolled-up jet and the fine slip line behind the Mach stem are where the
mesh refines most - exactly the small-scale features this benchmark is designed
to expose.
