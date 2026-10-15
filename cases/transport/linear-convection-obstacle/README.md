# Linear convection around an obstacle

A square profile is carried by a flow that goes around a solid obstacle. The
flow splits the profile in two, stretches both halves along the obstacle walls,
and joins them again downstream before they leave the domain. It shows how
samurai handles **immersed geometry**: the mesh is built on a domain with a
hole, and the adaptive mesh follows the thin layers that wrap the obstacle.

## Equation

We solve the linear convection equation

$$
\partial_t u + \nabla \cdot (\mathbf{a}\, u) = 0
$$

on the domain $[-1, 1]^2 \setminus [0, 0.4]^2$ (a square obstacle removed near
the center). The velocity derives from a stream function,

$$
\mathbf{a} = \left(\partial_y \psi,\; -\partial_x \psi\right), \qquad
\psi(x, y) = (x + y - 0.4)\left(1 - e^{-d(x, y)/\ell}\right),
$$

where $d$ is the distance to the obstacle and $\ell = 0.15$. Far from the
obstacle $\mathbf{a} = (1, -1)$. Since $\psi = 0$ on the obstacle boundary,
the wall is a streamline: no flow crosses it, and $\mathbf{a}$ is divergence
free, so the profile is transported without being compressed.

The initial profile is the square $[-0.5, -0.1] \times [0.5, 0.9]$, centered
on the streamline $x + y = 0.4$ that hits the obstacle head-on.

## Numerical method

- **Space:** fifth-order WENO5 convective flux (`make_convection_weno5`).
- **Time:** third-order TVD Runge-Kutta (SSPRK3). The time step follows the
  fastest cell, since the flow speeds up around the obstacle.
- **Adaptation:** multiresolution with threshold $\varepsilon = 10^{-3}$.
- **Geometry:** the domain is assembled with `DomainBuilder`. The boundary
  velocity is the flow itself (tangent to the obstacle, $(1, -1)$ on the outer
  boundary), so the profile leaves the domain through the outflow sides.

## What to look for

The profile wraps around the obstacle and splits into two streams that meet
again behind it. The finest cells sit on the thin layers along the obstacle
walls and on the fronts of the two streams; the rest of the domain stays
coarse.
