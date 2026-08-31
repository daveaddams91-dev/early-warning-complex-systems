"""
Unit tests verifying dynamical systems, analytical Jacobians, steady states,
eigenvalues, and theoretical variance formulas.
"""

import pytest
import numpy as np
from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem


def numerical_jacobian(f_func, x: np.ndarray, mu: float, eps: float = 1e-6) -> np.ndarray:
    """High-accuracy central finite-difference Jacobian approximation."""
    dim = len(x)
    f0 = f_func(x, mu)
    m = len(f0)
    jac = np.zeros((m, dim))
    for j in range(dim):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[j] += eps
        x_minus[j] -= eps
        f_plus = f_func(x_plus, mu)
        f_minus = f_func(x_minus, mu)
        jac[:, j] = (f_plus - f_minus) / (2.0 * eps)
    return jac


class TestMayHarvesting:
    def test_steady_state_and_jacobian(self):
        sys = MayHarvestingSystem(r=1.0, K=10.0, d=1.0)
        c_val = 2.0
        x_star = sys.steady_state(c_val)
        assert x_star.shape == (1,)
        # High stable biomass should be near 7.3166
        np.testing.assert_allclose(x_star[0], 7.3166, atol=1e-3)
        
        # Verify f(x*, c) approx 0
        f_val = sys.f(x_star, c_val)
        assert abs(f_val[0]) < 1e-5
        
        # Verify analytical Jacobian matches finite-difference
        j_analytical = sys.jacobian(x_star, c_val)
        j_numerical = numerical_jacobian(sys.f, x_star, c_val)
        np.testing.assert_allclose(j_analytical, j_numerical, atol=1e-4)

    def test_critical_slowing_down(self):
        sys = MayHarvestingSystem()
        # As c increases from 1.5 to 2.5, dominant eigenvalue (Jacobian value) must approach 0 from below
        eval_safe = np.real(sys.dominant_eigenvalue(1.5))
        eval_near = np.real(sys.dominant_eigenvalue(2.5))
        assert eval_safe < eval_near < 0.0
        
        # Theoretical variance must increase
        var_safe = sys.theoretical_variance(1.5, sigma=0.05)
        var_near = sys.theoretical_variance(2.5, sigma=0.05)
        assert var_near > var_safe > 0.0


class TestFitzHughNagumo:
    def test_hopf_bifurcation_eigenvalues(self):
        sys = FitzHughNagumoSystem()
        # Stable spiral for I = -0.5
        x_star = sys.steady_state(-0.5)
        j_ana = sys.jacobian(x_star, -0.5)
        j_num = numerical_jacobian(sys.f, x_star, -0.5)
        np.testing.assert_allclose(j_ana, j_num, atol=1e-4)
        
        # Check that real part of eigenvalues approaches 0 as I approaches I_crit ~ 0.331
        evals_safe = sys.eigenvalues(-0.5)
        evals_near = sys.eigenvalues(0.30)
        assert np.max(np.real(evals_safe)) < np.max(np.real(evals_near)) < 0.0
        # Imaginary part should be non-zero (oscillatory Hopf mode)
        assert abs(np.imag(evals_near[0])) > 0.1


class TestSubcriticalPitchfork:
    def test_analytical_properties(self):
        sys = SubcriticalPitchforkSystem()
        mu = -0.5
        x_star = sys.steady_state(mu)
        assert x_star[0] == 0.0
        j_ana = sys.jacobian(x_star, mu)
        assert j_ana[0, 0] == mu
        
        var_th = sys.theoretical_variance(mu, sigma=0.04)
        expected_var = (0.04**2) / (2.0 * abs(mu))
        np.testing.assert_allclose(var_th, expected_var, atol=1e-6)


class TestStommelBox:
    def test_steady_state_and_jacobian(self):
        sys = StommelBoxSystem()
        mu = 0.8
        x_star = sys.steady_state(mu)
        assert x_star.shape == (2,)
        assert x_star[0] > x_star[1]  # T > S thermal mode
        
        j_ana = sys.jacobian(x_star, mu)
        j_num = numerical_jacobian(sys.f, x_star, mu)
        np.testing.assert_allclose(j_ana, j_num, atol=1e-4)


class TestCoupledNetwork:
    def test_network_structure_and_jacobian(self):
        sys = CoupledNetworkSystem(n_nodes=6, network_type='erdos_renyi', seed=123)
        assert sys.dimension == 6
        mu = 1.5
        x_star = sys.steady_state(mu)
        assert len(x_star) == 6
        assert np.all(x_star > 0.0)
        
        j_ana = sys.jacobian(x_star, mu)
        j_num = numerical_jacobian(sys.f, x_star, mu)
        np.testing.assert_allclose(j_ana, j_num, atol=1e-3)
