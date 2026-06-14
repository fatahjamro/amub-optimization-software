# EXPERIMENTS.md

# Computational Experiments Protocol

This document details the configuration, parameters, and design of the experimental campaigns executed within the `amub-optimization-software` package.

---

## 1. Single-Seed Validation Sweep
*   **Purpose:** Serves as a positive control validation of the optimization pipeline across basis counts $n = 2, \ldots, 7$ in dimension $d = 6$.
*   **Configuration:** [single_seed_sweep.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/single_seed_sweep.yaml)
*   **Key Parameters:**
    *   `steps`: 10000 (standard), 50 (smoke-test)
    *   `seed`: 1234
    *   `learning_rate`: 0.02
    *   `initialization_scale`: 0.05
    *   `matrix_exp_backend`: `torch_native` (CPU), `taylor_matrix_exp` (GPU)
*   **Result Interpretation:** Verification that $n=2$ reaches exact MUB convergence ($\approx 10^{-31}$ loss), and $n=3$ converges to exact MUB, while higher basis counts exhibit nonzero defects.

---

## 2. Multi-Seed Optimization Campaigns
*   **Purpose:** To map the non-convex optimization landscape of dimension-six approximate MUBs and compile convergence statistics.
*   **Design:** 100 independent random seeds ($s \in \{0, 1, \dots, 99\}$) are optimized for $n \in \{3, 4, 5, 6\}$.
*   **HPC Configurations:**
    *   Double-Precision: [multiseed_janus_100.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/multiseed_janus_100.yaml)
    *   Single-Precision: [multiseed_janus_64.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/multiseed_janus_64.yaml)
*   **Key Parameters:**
    *   `steps`: 10000
    *   `learning_rate`: 0.02
    *   `initialization_scale`: 0.05

---

## 3. Precision Sensitivity Campaign
*   **Purpose:** Compare convergence accuracy and optimizer path stability between double precision (`complex128`) and single precision (`complex64`).
*   **Configurations:**
    *   [multiseed_complex128.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/multiseed_complex128.yaml)
    *   [multiseed_complex64.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/multiseed_complex64.yaml)
*   **Evaluation Metrics:** Compare minimum, median, and maximum losses, final unitarity residuals, and the sensitivity of "near-exact" pair classifications to different tolerance parameters ($10^{-4}$ vs. $10^{-6}$ vs. $10^{-8}$).

---

## 4. Hardware Performance Benchmarks
*   **Purpose:** Map the execution speed crossover point between standard CPU execution and hardware-accelerated GPU execution using the custom Taylor-series layer.
*   **Configuration:** [hardware_benchmarks.yaml](file:///Users/fatah/Documents/amub-optimization-software/configs/hardware_benchmarks.yaml)
*   **Key Parameters:**
    *   `dimensions`: $[6, 12, 24, 48, 96]$
    *   `steps`: 1000
    *   `dtypes`: `complex128` (CPU only) and `complex64` (CPU, MPS, CUDA)
*   **Measurements:** Total execution time (seconds) and average iteration step duration.

---

## 5. Quantum Hardware Verification
*   **Purpose:** Validate the classical mathematical optimal configurations on physical superconducting qubits.
*   **Target Configuration:** Optimized classical basis set for $d=6$, $n=4$ (seed 3).
*   **Experimental Circuit Structure:**
    *   For each pair $(i, j)$ of the 4 bases, we compute $W_{ij} = U_i^\dagger U_j$.
    *   We embed $W_{ij}$ (size $6 \times 6$) into a 3-qubit unitary $V_{ij} = W_{ij} \oplus I_2$ (size $8 \times 8$).
    *   We prepare the 6 computational states $|k\rangle \in \{|0\rangle, \dots, |5\rangle\}$ on 3 qubits, apply $V_{ij}$, and measure.
    *   This requires $6 \text{ pairs} \times 6 \text{ inputs} = 36$ distinct quantum circuits.
*   **Post-Selection Rules:** Measured outcomes resulting in states $|6\rangle$ (binary `110`) or $|7\rangle$ (binary `111`) are discarded because they lie outside the $d=6$ subspace. The remaining counts are renormalized.
