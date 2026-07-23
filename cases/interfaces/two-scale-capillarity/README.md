# Two-scale isothermal atomization

A liquid column is suddenly exposed to a fast air stream. The shear tears the
column apart, stretching it into ligaments that break into a fine spray. This
is the *separate-to-disperse* transition at the heart of primary atomization.

The case is the air-blasted liquid column of Section 5.2 of Orlando &
Massot, computed with a **unified two-scale two-phase model**: the same set of
equations describes both the resolved (large-scale) interface and an unresolved
(small-scale) disperse phase, and an inter-scale **mass transfer** moves liquid
from one representation to the other when the interface curvature exceeds a
threshold. This transfer is the main novelty of the model.

## Model

Both phases are isothermal and governed by a barotropic (linearized) equation
of state. The large-scale liquid is tracked through its volume fraction
$\alpha_\ell$, transported with the mixture and coupled to surface tension
through the capillary term $\sigma\,\kappa\,\mathbf{n}$, where the curvature
$\kappa$ and interface normal $\mathbf{n}$ are reconstructed from
$\nabla\alpha_\ell$:

$$
\partial_t (\rho \mathbf{u}) + \nabla\cdot(\rho\,\mathbf{u}\otimes\mathbf{u})
  + \nabla p = \nabla\cdot\big(\sigma\,(\|\nabla\alpha_\ell\|\,\mathbf{I}
  - \tfrac{\nabla\alpha_\ell\otimes\nabla\alpha_\ell}{\|\nabla\alpha_\ell\|})\big).
$$

Where the interface becomes too curved to resolve, a bound-preserving
relaxation transfers mass into a small-scale disperse volume fraction
$\alpha_d$, closing the separate-to-disperse cycle.

## Numerical method

- **Space:** second-order finite volumes; an HLLC solver for the hyperbolic
  subsystem and a dedicated flux for the surface-tension subsystem.
- **Time:** an operator-splitting, second-order (two-stage) scheme.
- **Relaxation:** a Newton-based, bound-preserving update of $\alpha_\ell$ that
  enforces the admissible-state bounds and drives the inter-scale mass transfer.
- **Adaptation:** samurai multiresolution refines the mesh along the interface
  and the freshly created ligaments.

## What to look for

Watch the liquid column (bright) flatten, wrap into a horseshoe and shed
ligaments downstream. The multiresolution mesh (grid overlay) chases the
interface, concentrating cells exactly where atomization happens and coarsening
in the quiescent gas.

## References

See `case.yaml` for the reference list.
