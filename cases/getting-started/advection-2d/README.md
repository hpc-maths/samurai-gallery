# Linear advection of a disc

This is the "hello world" of `samurai`: it transports a scalar field with a
constant velocity and lets the multiresolution mesh follow the solution.

## Equation

We solve the 2D linear advection equation

$$
\partial_t u + \mathbf{a} \cdot \nabla u = 0, \qquad \mathbf{a} = (a_x, a_y),
$$

on the unit square $[0, 1]^2$. The initial condition is the indicator function
of a disc of radius $r$ centered at $(x_c, y_c)$:

$$
u(x, y, 0) = \begin{cases} 1 & \text{if } (x - x_c)^2 + (y - y_c)^2 \le r^2, \\ 0 & \text{otherwise.} \end{cases}
$$

## Numerical method

- **Space:** first-order finite-volume upwind flux (`samurai::upwind`).
- **Time:** explicit forward Euler under a CFL constraint.
- **Adaptation:** multiresolution (`make_MRAdapt`) with threshold
  $\varepsilon = 2 \times 10^{-4}$. Cells are refined only near the sharp
  interface of the disc, so the bulk of the domain stays coarse.

## What to look for

The mesh concentrates its finest cells on the moving circular edge, where the
solution has its strongest gradients. This is the whole point of samurai: the
same accuracy as a fine uniform grid at a fraction of the cell count.

## Parameters

| Flag | Meaning | Default |
|------|---------|---------|
| `--velocity` | advection velocity $(a_x, a_y)$ | `1 1` |
| `--Tf` | final time | `0.6` |
| `--cfl` | CFL number | `0.5` |
| `--min-level` / `--max-level` | coarsest / finest MR level | `4` / `10` |
| `--mr-epsilon` | multiresolution threshold | `2e-4` |
