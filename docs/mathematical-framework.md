# Mathematical Framework & Indicator Formulations

This document details the analytical formulations for all stochastic dynamical systems, normal forms, and early-warning indicators implemented in this repository.

---

## 1. Stochastic Differential Equations & Bifurcation Normal Forms

### 1.1 May Harvesting Model (Fold / Saddle-Node Bifurcation)
$$\frac{dx}{dt} = r x \left(1 - \frac{x}{K}\right) - c \frac{x^2}{x^2 + d^2} + \sigma dW_t$$
- **Parameters**: $r = 1.0, K = 10.0, d = 1.0$.
- **Bifurcation Point**: $c_c \approx 2.6044$.
- **Analytical Jacobian**:
  $$J(x, c) = r\left(1 - \frac{2x}{K}\right) - \frac{2cd^2 x}{(x^2 + d^2)^2}$$
- **Equilibria**: Non-zero steady states are roots of the cubic polynomial:
  $$x^3 - K x^2 + \left(\frac{cK}{r} + d^2\right) x - K d^2 = 0$$

### 1.2 FitzHugh-Nagumo Model (Supercritical Hopf Bifurcation)
$$\begin{aligned}
\frac{dv}{dt} &= v - \frac{v^3}{3} - w + I_{\text{ext}} + \sigma dW_{1,t} \\
\frac{dw}{dt} &= \epsilon (v + a - b w) + \sigma dW_{2,t}
\end{aligned}$$
- **Parameters**: $\epsilon = 0.08, a = 0.7, b = 0.8$.
- **Bifurcation Point**: $I_c \approx 0.332$ where $\mathrm{Tr}(\mathbf{J}) = 0$ and $\det(\mathbf{J}) > 0$.
- **Analytical Jacobian**:
  $$\mathbf{J}(v, w) = \begin{pmatrix} 1 - v^2 & -1 \\ \epsilon & -\epsilon b \end{pmatrix}$$

### 1.3 Subcritical Pitchfork Model
$$\frac{dx}{dt} = \mu x + x^3 - x^5 + \sigma dW_t$$
- **Bifurcation Point**: $\mu_c = 0.0$.
- **Jacobian at Origin**: $J(0, \mu) = \mu$.

### 1.4 Stommel 2-Box Thermohaline Ocean Model
$$\begin{aligned}
\frac{dT}{dt} &= \eta_1 (T_e - T) - |T - S| T \\
\frac{dS}{dt} &= \eta_2 (S_e - S) - |T - S| S + \sigma dW_t
\end{aligned}$$
- **Advective Flow Rate**: $\Phi = |T - S|$.
- **Bifurcation**: Fold bifurcation resulting in Atlantic Meridional Overturning Circulation (AMOC) collapse.

### 1.5 Coupled Mutualistic Ecological Network (10-Node)
$$\frac{dx_i}{dt} = r_i x_i \left(1 - \frac{x_i}{K_i}\right) + \sum_{j=1}^N \frac{\gamma A_{ij} x_j}{1 + h \sum_k A_{ik} x_k} - c \frac{x_i^2}{x_i^2 + d^2} + \sigma dW_{i,t}$$
- **Parameters**: $r = 1.0, K = 10.0, \gamma = 0.2, h = 0.1, d = 1.0$.
- **Topology**: Erdős-Rényi random graph ($N=10, p=0.4$).

---

## 2. Mathematical Indicator Formulations

### 2.1 Univariate Indicators
1. **Sample Variance**:
   $$\hat{\sigma}^2_t = \frac{1}{W - 1} \sum_{i=0}^{W-1} (x_{t-i} - \bar{x}_t)^2$$
2. **Lag-1 Autocorrelation (AR(1))**:
   $$\hat{\rho}_{1,t} = \frac{\sum_{i=0}^{W-2} (x_{t-i} - \bar{x}_t)(x_{t-i-1} - \bar{x}_t)}{\sum_{i=0}^{W-1} (x_{t-i} - \bar{x}_t)^2}$$
3. **Bandt-Pompe Permutation Entropy**:
   $$H_{\text{perm}} = -\frac{1}{\ln(m!)} \sum_{\pi \in \mathcal{S}_m} p(\pi) \ln p(\pi)$$
4. **Spectral Reddening**:
   $$S_{\text{low}} = \frac{\int_0^{0.2 f_N} P(f) df}{\int_0^{f_N} P(f) df}$$

### 2.2 Multivariate Indicators
1. **Principal Component Leading Variance**:
   $$\lambda_1(\mathbf{C}_t) = \max_{\|\mathbf{v}\|=1} \mathbf{v}^T \mathbf{C}_t \mathbf{v}$$
2. **Multi-Indicator Mahalanobis Distance**:
   $$D_M(\mathbf{S}_t) = \sqrt{(\mathbf{S}_t - \bar{\mathbf{S}}_0)^T (\mathbf{\Sigma}_S + \epsilon \mathbf{I})^{-1} (\mathbf{S}_t - \bar{\mathbf{S}}_0)}$$
