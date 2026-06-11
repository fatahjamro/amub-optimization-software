# Peer Review Report & Recommendations

**Manuscript Title:** A Generalized Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six  
**Target Journal:** *Quantum*  
**Reviewer Report:** Section-by-Section Analysis and Recommendations

---

## 1. Executive Summary
The manuscript introduces a parameterized, dimension-agnostic software workflow to optimize and study approximate mutually unbiased basis (AMUB) configurations. It uses an unanchored formulation under Lie-algebra unitary parameterization, optimized via PyTorch's automatic differentiation. The authors apply this workflow as a case study to the open problem in dimension six ($d=6$), conducting a 100-seed numerical campaign for basis counts $n=3,4,5,6$. Additionally, they address hardware-acceleration portability constraints on GPU backends lacking native complex matrix exponentials by designing a custom Taylor-series matrix exponentiation layer.

### Major Strengths:
1. **Unanchored Formulation:** Optimizing all bases symmetrically rather than anchoring one basis is a very natural formulation that lets symmetric structure (e.g., defective hubs) emerge organically rather than imposing them.
2. **Computational Rigor:** The transition to a 100-seed campaign on the JANUS cluster provides the statistical weight needed for a reputable quantum computing journal.
3. **Hardware Portability & Benchmarking:** Documenting the Taylor-series fallback performance on both consumer hardware (M1 Mac) and HPC hardware (NVIDIA A100 GPU) makes the technical scaling story highly convincing.
4. **Reproducibility:** Excellent documentation of hyperparameters, dynamic norm warning safeguards, and the structured file export policy.

---

## 2. Section-by-Section Review & Recommendations

### Title & Abstract
*   **Comments:** The title is clear and accurately represents the work. The abstract provides a concise, quantitative summary of the key findings (exactness at $n \le 4$, transition to global defect at $n \ge 5$, precision impacts, and GPU performance crossover).
*   **Recommendation:**
    *   *Minor Clarification:* Ensure "dimension ninety" in the abstract matches the text. (The text states a crossover "near $d \approx 80$" and benchmarks up to $d=96$; explicitly stating "crossover around $d \approx 80$ (benchmarked to $d=96$)" is more precise).

### Section 1: Introduction
*   **Comments:** Well-written context. It sets up the $d=6$ MUB puzzle, introduces the unanchored and Lie-algebraic approach, and mentions the precision comparison.
*   **Recommendation:**
    *   *Citation context:* When mentioning other analytic and computational approaches in line 47, add a sentence acknowledging that past computer-assisted searches (such as those by Szöllősi, Brierley/Bengtsson) focused on *anchored* searches or specific families of Hadamard matrices (e.g. Fourier family). This helps contrast and justify why the *unanchored* formulation is a novel contribution.

### Section 2: Contributions
*   **Comments:** The section clearly outlines the contributions of the paper.
*   **Recommendation:**
    *   Ensure alignment: Ensure the mention of "100 independent random seeds" in Section 2 is consistently stated (which it is, matching the updated text).

### Section 3: Mathematical Formulation
*   **Comments:** The formulation is mathematically sound. The unanchored optimization description is clear, and the Lie-algebra parameterization $U = \exp(iH)$ is standard and appropriate for maintaining unitarity.
*   **Recommendation:**
    *   *Symmetrization detail:* In Equation (13), the generator is written as $H_k = (A_k + A_k^\dagger)/2$. Note that this formulation uses $36$ complex parameters (72 real values) to represent a space of Hermitian matrices which has dimension $d^2 = 36$ real parameters. It might be worth adding a one-sentence footnote or comment acknowledging that this is a redundant parameterization but is numerically stable and well-suited for standard gradient-based optimizers without needing manifold projections.

### Section 4: Software Workflow and Precision Policy
*   **Comments:** The section is strong, particularly in how it documents the Taylor-series truncation error bound.
*   **Recommendation:**
    *   *Unitarity check:* For the Taylor series GPU run, emphasize that since $T_N(iH)$ is not strictly unitary in float precision, the unitarity residual $\|U_k^\dagger U_k - I\|_F$ is monitored and remains extremely small ($<10^{-9}$ for A100/MPS runs). This addresses a common reviewer question about whether Taylor approximation breaks unitarity.

### Section 5: Experimental Methodology
*   **Comments:** Good detail. Table 3 (Hyperparameters) contains a small legacy line: "Campaign seed set ($s$) | $\{0, 1, 2, 3, 4\}$" from the older 5-seed runs.
*   **Recommendation:**
    *   *CRITICAL FIX:* Table 3 (Table 4 in the updated pdf) has a row: `Campaign seed set (s) | {0, 1, 2, 3, 4}`. Since the campaigns were upgraded to 100 seeds ($s \in \{0, \ldots, 99\}$), this row **must be updated** to avoid confusing the reader. It should say `Campaign seed set (s) | {0, 1, ..., 99}`.

### Section 6: Results
*   **Comments:** The results section is extensive and the addition of the JANUS A100 GPU benchmark (Table 6) alongside the M1 Mac GPU benchmark (Table 5) provides an excellent hardware scalability comparison.
*   **Recommendation:**
    *   *Crossover discussion:* Discuss the difference between the GPU crossover on M1 Mac (crossover around $d \approx 80$) and the JANUS NVIDIA A100 cluster (crossover between $d=24$ and $d=48$). Explain that the NVIDIA A100 has much higher raw compute capacity but also different kernel launch overheads, allowing the hardware crossover to occur at smaller dimensions compared to consumer-grade Apple Silicon.

### Section 7: Conclusion & Appendix
*   **Comments:** The conclusions are grounded and avoid overclaiming. The appendix figures are clear and provide the reader with a detailed look at the loss spectrum.
*   **Recommendation:**
    *   *Open Source:* Add a sentence stating where the codebase and data artifacts are hosted (or will be hosted) to strengthen the reproducibility claim.

---

## 3. Actionable Software & Script Recommendations

To ensure the codebase matches the academic quality of the reframed paper:

1.  **Dynamic Parameter CLI Overrides:**
    *   Ensure `scripts/run_single_seed_sweep.py` and `scripts/run_multiseed_campaign.py` support `--dimension` (`-d`) and `--n-bases` arguments to make the CLI fully dimension-agnostic.
2.  **Adaptive Taylor Safeguard:**
    *   The Taylor-series generator in `src/amub/taylor_exp.py` prints a warning if the norm is large. Make sure this checks the Frobenius norm of $H$ and suggests higher orders if needed.
3.  **Visualization Scale:**
    *   Ensure plotting functions in `src/amub/plotting.py` dynamically adjust fonts and color schemes if the user runs simulations with $d > 6$ or $n > 6$.