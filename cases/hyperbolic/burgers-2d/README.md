# Burgers equation (2D)

The vector Burgers equation extends the 1D shock-forming dynamics to two
dimensions. It is a compact, nonlinear stress test for the adaptive mesh.

## Equation

For the velocity field $\mathbf{u} = (u, v)$ we solve

$$
\partial_t \mathbf{u} + \nabla \cdot \left( \tfrac{1}{2}\, \mathbf{u} \otimes \mathbf{u} \right) = 0,
\qquad (x, y) \in [-1, 1]^2.
$$

The initial condition is a radial "hat": each component equals
$\max\!\left(0, 1 - r/0.5\right)$ with $r = \sqrt{x^2 + y^2}$.

## Numerical method

- **Space:** fifth-order WENO5 flux (`make_convection_weno5`).
- **Time:** third-order TVD Runge-Kutta (SSPRK3).
- **Adaptation:** multiresolution.

The image shows the velocity magnitude $|\mathbf{u}|$.

## What to look for

The smooth radial bump collapses and its trailing edge steepens into sharp
fronts. The mesh refines along those fronts and stays coarse elsewhere.
