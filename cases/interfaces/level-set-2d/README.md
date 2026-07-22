# Level-set in a vortex flow

This is the classic "vortex in a box" benchmark for interface capturing. A
circular interface is represented implicitly as the zero level of a signed
distance function $\phi$, and advected by a swirling, incompressible velocity
field that stretches it into a thin filament.

## Equation

The level set $\phi$ is transported by the velocity $\mathbf{u}$:

$$
\partial_t \phi + \mathbf{u} \cdot \nabla \phi = 0,
$$

with the single-vortex velocity field

$$
\mathbf{u}(x, y) = \big(-\sin^2(\pi x)\,\sin(2\pi y),\; \sin^2(\pi y)\,\sin(2\pi x)\big).
$$

The interface is the set $\{\phi = 0\}$, initially a circle of radius $0.15$
centered at $(0.5, 0.75)$.

## Numerical method

- **Transport:** upwind scheme for a variable velocity field, with a
  multiresolution **flux correction** at level interfaces.
- **Reinitialization:** a few fictitious TVD-RK2 steps solving
  $|\nabla \phi| = 1$ keep $\phi$ a signed distance near the interface.
- **Adaptation:** multiresolution driven by a sharp marker across the
  interface, so the finest cells hug the front.

## What to look for

The blue region ($\phi < 0$) is the interior of the interface. It is drawn out
into an ever-thinner spiral filament; the adaptive mesh refines all along it,
which is exactly where a uniform grid would be prohibitively expensive.
