# 📊 AMUB Computational Results and Hardware Analysis

This document summarizes the expected behaviors of our optimization scripts and details the actual mathematical and hardware performance achievements obtained on different devices.

---

## 1. Expected Behaviors of Runner Scripts

*   **`run_single_seed_sweep.py`**
    *   *Expectation:* Validates the workflow sequentially from $n=2$ up to $n=7$ bases using a fixed validation seed (default $1234$). It serves as a positive control.
    *   *Result:* Confirms that the optimizer easily resolves the trivial $n=2$ case to a loss of $\approx 10^{-31}$ (machine zero) and successfully runs the complete-set target $n=7$.
*   **`run_multiseed_campaign.py`**
    *   *Expectation:* Explores the nonconvex landscape by running 100 independent random seeds ($s \in \{0, 1, \ldots, 99\}$). It is executed for both `complex128` (double precision) and `complex64` (single precision) to identify basin selection and convergence statistics.
*   **`run_hardware_benchmarks.py`**
    *   *Expectation:* Compares the computational speed (execution time for 1000 steps) across dimensions $d \in \{6, 12, 24, 48, 96\}$ on CPU vs. GPU. It evaluates CPU native `torch.matrix_exp` against the custom Taylor-series matrix exponentiation layer on the GPU.
*   **`summarize_results.py`**
    *   *Expectation:* Aggregates the 100-seed directories to output statistical summaries (minimum, median, maximum losses, and near-exact pair counts under various tolerances).
*   **`generate_figures.py`**
    *   *Expectation:* Reads the aggregated JSON results to output publication-quality matplotlib plots for the manuscript's appendix.

---

## 2. Mathematical Discoveries in Dimension Six ($d=6$)

Our 100-seed campaigns revealed a structured, robust transition in the unanchored MUB landscape:

1.  **Exact Triples ($n=3$):** 
    *   *Achieved:* The optimizer consistently recovers exact MUB configurations. The median best loss is extremely close to machine zero ($\sim 10^{-31}$ in double precision), and all 3 pairwise overlap matrices satisfy the unbiasedness condition perfectly.
2.  **Hub-and-Triangle Structure ($n=4$):**
    *   *Achieved:* The optimizer recovers a highly structured basin. Out of the 6 basis pairs, exactly 3 pairs are near-exact (losses $< 10^{-30}$), forming a star-like "hub" geometry. The remaining 3 pairs form a localized, defective triangle where the pairwise losses are identical and non-zero ($\approx 0.0555$).
3.  **Transition to Global Defect ($n \ge 5$):**
    *   *Achieved:* For $n=5$ and $n=6$, **no near-exact pairs are found** under the primary tolerance of $10^{-6}$. Instead, the configurations become globally defective:
        *   For $n=5$, all 10 pairwise losses are non-zero.
        *   For $n=6$, all 15 pairwise losses are non-zero, with structured, repeated loss levels.
    *   This confirms that increasing the candidate basis count forces the optimizer out of exact pairwise relationships and into globally distributed defect.

---

## 3. Impact of Numerical Floating-Point Precision

We compared the reference double-precision (`complex128`) against single-precision (`complex64`) on CPU:
*   **Basin Selection:** Double precision is far more effective at resolving fine-grained minima. In `complex64`, roundoff error limits the optimizer's ability to settle into the exact low-loss valleys, and the runs are susceptible to basin selection effects (frequently getting trapped in higher-loss local minima).
*   **Tolerance Sensitivity:** In single-precision, the lower numerical resolution causes maximum deviations $\delta_{ij}$ to cluster around $10^{-4}$ to $10^{-6}$. As a result, counting near-exact pairs in `complex64` is highly sensitive to the chosen tolerance threshold, whereas `complex128` results remain stable across different tolerances.
*   **Unitarity Residuals:** Unitarity residuals in `complex128` are bounded around $10^{-15}$ (close to double-precision machine epsilon), while in `complex64` they scale up to $10^{-7}$.

---

## 4. Hardware Scaling and Acceleration Crossover

We benchmarked iteration speeds on both consumer workstation (Apple M1) and high-performance computing cluster (JANUS, featuring AMD EPYC CPUs and NVIDIA A100 GPUs) hardware.

### Workstation (Apple M1 CPU vs. MPS GPU):
*   **Small Dimensions ($d \le 48$):** The workstation CPU is faster. For example, at $d=6$, the CPU completes 1000 steps in 2.6 seconds, while the MPS GPU requires 43 seconds. This is because the arithmetic workload is too small to amortize the GPU's fixed Metal API and kernel launch overheads.
*   **Crossover Point:** A performance crossover occurs around **dimension 80**. At $d=96$, the MPS GPU is faster than the double-precision CPU baseline ($48.4$ seconds vs. $62.3$ seconds, achieving a $1.29\times$ speedup).

### HPC Cluster (AMD EPYC CPU vs. NVIDIA A100 GPU):
*   **Crossover Point:** The crossover occurs much earlier on the cluster, **between $d=24$ and $d=48$**. At $d=96$, the A100 GPU achieves a **$2.63\times$ speedup** relative to the double-precision CPU reference ($27.7$ seconds vs. $72.8$ seconds).
*   **Explanation:** While both GPUs exhibit flat timing curves dominated by scheduling latencies (26–28s on A100 vs. 43–45s on M1), the massive parallel compute power of the NVIDIA A100 allows it to amortize these overheads and beat the CPU at a much lower dimensionality.
*   **Taylor Unitarity:** Unitarity residuals on both GPU backends (running the order-20 Taylor layer) remained consistently below $10^{-9}$, verifying that the Taylor approximation does not degrade the mathematical unitarity of the bases.
