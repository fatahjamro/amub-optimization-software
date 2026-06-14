# Peer Review Report & Recommendations

**Manuscript Title:** A Generalized Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six  
**Target Journal:** *Quantum*  
**Reviewer Report:** Section-by-Section Analysis and Recommendations

---

## 1. Executive Summary
The manuscript introduces a parameterized, dimension-agnostic software workflow to optimize and study approximate mutually unbiased basis (AMUB) configurations. It uses an unanchored formulation under Lie-algebra unitary parameterization, optimized via PyTorch's automatic differentiation. The authors apply this workflow as a case study to the open problem in dimension six ($d=6$), conducting a 100-seed numerical campaign for basis counts $n=3,4,5,6$. 

In the latest revision, the authors have integrated a physical **Quantum QPU Verification** section, executing the optimized $d=6, n=4$ unanchored AMUB configuration on the 156-qubit Heron processor `ibm_marrakesh`. Additionally, they address hardware-acceleration portability constraints on GPU backends by designing a custom Taylor-series matrix exponentiation layer.

### Major Strengths:
1. **Unanchored Formulation:** Optimizing all bases symmetrically rather than anchoring one basis is a very natural formulation that lets symmetric structure (e.g., defective hubs) emerge organically.
2. **Computational Rigor:** The transition to a 100-seed campaign on the JANUS cluster provides the statistical weight needed for a reputable quantum computing journal.
3. **Physical QPU Validation:** Testing the optimized $d=6, n=4$ unitaries on real quantum hardware bridges the gap between classical numerical design and physical execution. The subspace post-selection (discarding $|6\rangle$ and $|7\rangle$ leakage states) is mathematically correct and well-suited.
4. **Reproducibility:** Excellent documentation of hyperparameters, dynamic norm warning safeguards, and the structured file export policy.

---

## 2. Section-by-Section Review & Recommendations

### Title & Abstract
*   **Comments:** The title is clear and represents the work. The abstract provides a concise, quantitative summary of key findings (including the classical results, precision effects, GPU crossovers, and physical QPU validation).
*   **Recommendation:**
    *   *Minor Clarification:* Mention in the abstract that the classically optimized bases have been verified on physical IBM Quantum hardware, confirming the gate-noise limits on NISQ processors.

### Section 1: Introduction
*   **Comments:** Well-written context. It sets up the $d=6$ MUB puzzle, introduces the unanchored approach, and mentions the physical QPU verification.
*   **Recommendation:**
    *   *Citation context:* When mentioning other analytic and computational approaches, add a sentence acknowledging that past computer-assisted searches (such as those by Szöllősi, Brierley/Bengtsson) focused on *anchored* searches or specific families of Hadamard matrices. This helps contrast and justify why the *unanchored* formulation is a novel contribution.

### Section 3: Mathematical Formulation
*   **Comments:** The formulation is mathematically sound. The Lie-algebra parameterization $U = \exp(iH)$ is standard and appropriate.
*   **Recommendation:**
    *   *Symmetrization detail:* In Equation (13), the generator is written as $H_k = (A_k + A_k^\dagger)/2$. This formulation uses $36$ complex parameters (72 real values) to represent a space of Hermitian matrices which has dimension $d^2 = 36$ real parameters. Acknowledge in a brief footnote that this is a redundant parameterization but is numerically stable and well-suited for standard gradient-based optimizers without needing manifold projections.

### Section 4: Software Workflow and Precision Policy
*   **Comments:** The section is strong, particularly in how it documents the Taylor-series truncation error bound.
*   **Recommendation:**
    *   *Unitarity check:* For the Taylor series GPU run, emphasize that since $T_N(iH)$ is not strictly unitary in float precision, the unitarity residual is monitored and remains extremely small ($<10^{-9}$ for A100/MPS runs).

### Section 5: Experimental Methodology
*   **Comments:** Good detail. Table 3 (Hyperparameters) contains a small legacy line: "Campaign seed set ($s$) | $\{0, 1, 2, 3, 4\}$".
*   **Recommendation:**
    *   *CRITICAL FIX:* Table 3 has a row: `Campaign seed set (s) | {0, 1, 2, 3, 4}`. Since the campaigns were upgraded to 100 seeds ($s \in \{0, \ldots, 99\}$), this row **must be updated** to say `Campaign seed set (s) | {0, 1, ..., 99}`.

### Section 6: Results (Including QPU Verification)
*   **Comments:** The QPU verification section on `ibm_marrakesh` provides an excellent look at physical execution limits.
*   **Weakness & Recommendation:**
    *   *Explain the "Noise Floor" and compilation depth:* The physical losses for the exact pairs ($\approx 0.024 - 0.076$) and defective pairs ($\approx 0.048 - 0.070$) overlap, which blurs the classical "hub-and-triangle" gap. The manuscript correctly attributes this to the compilation depth (37 CZ gates and ~150 single-qubit gates per unitary). **Recommendation:** Add a sentence noting that since a general 3-qubit unitary has 63 degrees of freedom, compiling it onto a linear-topology Heron chip generically requires a deep 2-qubit gate sequence. This explains why the noise is uniform across all 6 pairs.
    *   *Quantum Error Mitigation (QEM) Discussion:* Reviewers for *Quantum* will ask why no error mitigation was used. **Recommendation:** Add a brief paragraph in the Discussion or Conclusion section stating that while the physical results are dominated by gate noise under simple post-selection, future work will integrate advanced QEM techniques (such as Pauli Twirling, Zero-Noise Extrapolation, or Readout Mitigation) to resolve the classical defect structures.

### Section 7: Conclusion & Appendix
*   **Comments:** The conclusions are grounded and avoid overclaiming.
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