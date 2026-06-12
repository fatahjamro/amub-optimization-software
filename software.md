# 💻 AMUB Software Workflow Technical Documentation

This document provides a step-by-step explanation of the software architecture and optimization pipeline developed in the `d6mubOptimization-v2` repository. The code is written in Python/PyTorch and is designed to be fully dimension-agnostic ($d$) and basis-count-agnostic ($n$).

---

## 1. Core Mathematical Components

### Lie-Algebra Unitary Parameterization (`src/amub/model.py`)
To guarantee that the optimized bases remain strictly unitary throughout the optimization without needing projection steps or penalty terms, the software parameterizes each basis $U_k$ using Lie-algebra exponentiation:
1. **Unconstrained Parameterization:** For each basis, we define a trainable complex matrix $A_k \in \mathbb{C}^{d \times d}$.
2. **Hermitian Generator Symmetrization:** The generator matrix $H_k$ is constructed by symmetrizing $A_k$:
   $$H_k = \frac{A_k + A_k^\dagger}{2}$$
   This discards the anti-Hermitian component, ensuring $H_k$ is strictly Hermitian ($H_k = H_k^\dagger$) by construction.
3. **Unitary Mapping:** The unitary matrix is generated via skew-Hermitian exponentiation:
   $$U_k = \exp(iH_k)$$
   In exact arithmetic, $U_k$ is guaranteed to be unitary.

### Loss Function (`src/amub/loss.py`)
The optimization objective measures the entrywise squared modulus deviation from the mutually unbiased basis condition.
1. **Pairwise Overlap:** For a pair of bases $U_i$ and $U_j$, the transition matrix squared moduli are computed entrywise:
   $$M_{ij} = |U_i^\dagger U_j|^2$$
2. **Pairwise Loss:** The defect of the pair is the squared Frobenius norm deviation from the target value $1/d$:
   $$\ell_{ij} = \left\| M_{ij} - \frac{1}{d} \mathbf{1}_{d \times d} \right\|_F^2 = \sum_{a,b=1}^d \left( |(U_i^\dagger U_j)_{ab}|^2 - \frac{1}{d} \right)^2$$
3. **Total Loss:** The total loss is the sum over all unordered pairs:
   $$\mathcal{L}_n = \sum_{1 \le i < j \le n} \ell_{ij}$$

---

## 2. Hardware Acceleration and Matrix Exponentiation Routing

### Custom Taylor-Series Layer (`src/amub/taylor_exp.py`)
The Lie-algebra parameterization requires evaluating the complex matrix exponential $\exp(iH)$. PyTorch's native `torch.matrix_exp` is not implemented on the Apple Silicon GPU (MPS) backend and can encounter limitations on other accelerators for complex datatypes. 

To overcome this, we developed a customized, differentiable Taylor-series matrix exponentiation layer:
$$T_N(X) = \sum_{m=0}^{N} \frac{X^m}{m!}$$

#### Safety Safeguards:
1. **Truncation Bound:** The truncation error in the spectral norm is bounded by:
   $$\| \exp(X) - T_N(X) \|_2 \le \frac{\|X\|_2^{N+1}}{(N+1)!} e^{\|X\|_2}$$
2. **Dynamic Norm Monitoring:** The function computes the Frobenius norm of the generator matrix $X = iH$. If the norm exceeds $3.0$, a `RuntimeWarning` is raised, alerting the user to increase the Taylor order $N$ (default $N=20$) or reduce the learning rate to maintain precision.
3. **Device Routing:** 
   * **CPU:** Automatically routes to PyTorch's native double-precision `torch.matrix_exp(1j * H)` reference implementation.
   * **GPU (MPS/CUDA):** Employs the custom Taylor-series layer (`taylor_matrix_exp`) to enable hardware acceleration without CPU fallback.

---

## 3. Post-Processing and Diagnostics (`src/amub/diagnostics.py`)

At the end of each optimization run, the best basis configurations are analyzed using several diagnostic metrics:
1. **Unitarity Residuals:** Quantifies the deviation from unitarity due to floating-point roundoff and Taylor truncation:
   $$\epsilon_k = \|U_k^\dagger U_k - I_d\|_F$$
2. **Maximum Absolute Deviation ($\delta_{ij}$):** Measures the worst-case entrywise deviation from $1/d$:
   $$\delta_{ij} = \max_{a,b} \left| |(U_i^\dagger U_j)_{ab}|^2 - \frac{1}{d} \right|$$
3. **Near-Exact Pair Classification:** Classified as "near-exact" if $\delta_{ij} < \tau$ (primary tolerance $\tau = 10^{-6}$).

---

## 4. Execution Step-by-Step

A standard run proceeds as follows:
1. **Initialization:** The runner script reads parameters (dimension $d$, number of bases $n$, dtype, random seed, steps) from config YAML files or CLI overrides.
2. **Model Setup:** Instantiates the `UnanchoredAMUBModel` with $n$ trainable bases in dimension $d$. Weights are initialized using a small Gaussian scale (default $0.05$).
3. **Optimization Loop:**
   * In each step, the optimizer (Adam, learning rate $0.02$) computes the forward pass: evaluates the unitary matrices $U_k$ (routing through native exp on CPU or Taylor exp on GPU) and computes the total loss $\mathcal{L}_n$.
   * Backward pass computes gradients via autograd.
   * Optimizer updates the unconstrained parameters $A_k$.
   * The model monitors and saves the configuration that achieves the lowest loss value seen during the run.
4. **Artifact Export:** The best basis matrices, overlap tensors, unitarity residuals, optimization history, and run metadata are exported to a structured folder under `results/` for full reproducibility.
