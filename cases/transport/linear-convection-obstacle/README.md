# Linear convection around an obstacle

A square profile is transported by a constant diagonal velocity across a domain
that contains a solid obstacle. It shows how samurai handles **immersed
geometry**: the mesh is built on a domain with a hole, and the boundary of the
obstacle is treated as a wall.

## Equation

We solve the linear convection equation

$$
\partial_t u + \mathbf{a} \cdot \nabla u = 0, \qquad \mathbf{a} = (1, -1),
$$

on the domain $[-1, 1]^2 \setminus [0, 0.4]^2$ (a square obstacle removed from
the center). The initial profile is a unit square in the upper-left region.

## Numerical method

- **Space:** fifth-order WENO5 convective flux (`make_convection_weno5`).
- **Time:** third-order TVD Runge-Kutta (SSPRK3).
- **Adaptation:** multiresolution with threshold $\varepsilon = 10^{-3}$.
- **Geometry:** the domain is assembled with `DomainBuilder`, and a wall
  boundary condition is imposed on the obstacle.

## What to look for

The profile travels toward the lower-right and splits around the obstacle. The
adaptive mesh tracks both the moving fronts and the wake near the obstacle
corners, while the interior stays coarse.
