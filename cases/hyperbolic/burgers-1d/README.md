# Burgers equation (1D)

The inviscid Burgers equation is the simplest nonlinear conservation law that
develops a **shock** from smooth initial data. It is the classic first step
before compressible Euler.

## Equation

$$
\partial_t u + \partial_x \left( \tfrac{1}{2} u^2 \right) = 0, \qquad x \in [-1, 1].
$$

The initial condition is a triangular "hat":

$$
u(x, 0) = \max\left(0,\; 1 - \frac{|x|}{r}\right), \qquad r = 0.5.
$$

## Numerical method

- **Space:** fifth-order WENO5 flux (`make_convection_weno5`) on the Burgers
  flux $f(u) = u^2/2$.
- **Time:** third-order TVD Runge-Kutta (SSPRK3).
- **Adaptation:** multiresolution, refining down to level 9.

## What to look for

The right side of the hat steepens until it becomes a discontinuity (a shock),
while the left side spreads into a rarefaction. The blue dots mark cell centers:
they cluster tightly at the shock and stay sparse in the smooth regions.
