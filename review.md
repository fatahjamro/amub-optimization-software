
# 💻 Software Generalization Review and Recommendations

The core library (`src/amub`) is already mathematically dimension-agnostic. The model definition `UnanchoredAMUBModel` in `model.py` and the loss calculation in `loss.py` accept the dimension $d$ and number of bases $n$ as parameters and construct matrices accordingly.

However, to align the software with the reframed "generalized workflow" story, we recommend the following minimalist updates to the runner scripts and configurations:

## 1. CLI Override for Dimension and Basis Count
Currently, runner scripts like `scripts/run_single_seed_sweep.py` and `scripts/run_multiseed_campaign.py` read parameters entirely from static YAML files.
*   **Recommendation:** Add optional `--dimension` (`-d`) and `--n-bases` argparse arguments to `scripts/run_single_seed_sweep.py` and `scripts/run_multiseed_campaign.py` to allow users to run arbitrary dimensional sweeps directly from the terminal without editing configuration files.

## 2. Dynamic Taylor Order Safety Check
Our custom GPU-accelerated exponentiation layer uses a fixed Taylor series expansion order ($N=20$) in `src/amub/taylor_exp.py`. While highly accurate for the dimension six generators ($\|H\|_2 \approx 2.7$), higher dimensions or larger step sizes may produce generators with larger norms, causing the truncation error to grow.
*   **Recommendation:** Implement a warning or adaptive order mechanism in `src/amub/taylor_exp.py` if the input generator matrix norm $\|X\|_2$ exceeds a threshold (e.g. $\|X\|_2 > 3.0$), protecting truncation bounds in generalized, higher-dimensional searches.

## 3. Generalize the Diagnostic and Plotting Utilities
Certain functions in `src/amub/plotting.py` might contain layout or style elements optimized primarily for $d=6$ or small values of $n$.
*   **Recommendation:** Verify that color mappings, axis limits, and annotations scale gracefully when $d \ge 10$ or when the number of bases $n \ge 8$. Ensure labels and layout parameters are dynamically sized.

## How to frame the Narrative in the Paper (Local vs. HPC)
Our suggested structure is excellent and very professional. We can frame the paper like this:

- Development and Prototyping Phase (Local):
We developed the unanchored approximate MUB model in Python/PyTorch.
To support local hardware-accelerated development on Apple Silicon GPUs (MPS), where complex matrix exponentials are natively missing in PyTorch, we developed and validated the custom Taylor-series matrix exponentiation layer as a portable fallback.
- Production and Scaling Phase (HPC Cluster):
To run robust, large-scale sweeps (100 seeds for both complex128 and complex64), we deployed the software on ATU's JANUS HPC cluster.
On JANUS CPU nodes, we run native, double-precision and single-precision operations.
The framework is fully compatible with NVIDIA CUDA GPUs on clusters, where it natively utilizes CUDA's highly optimized complex linear algebra operations without requiring the Taylor fallback.

---

# 📝 Comparative Analysis & Manuscript Enhancements (100-Seed HPC Data)

Running 100 seeds for both `complex128` and `complex64` on JANUS requires us to adjust the tables in the paper to accommodate this larger dataset. Currently, some columns list individual seed counts (e.g. `3,3,0,3,0` for 5 seeds), which cannot scale to 100 seeds.

We propose the following minimalist changes to the paper's manuscript:

## 1. Table Reformatting (Aggregated Metrics)
Instead of listing individual seed counts (like `3,3,0,3,0`), we will reformat the tables to use aggregated metrics:
*   **Table 1 (`tab:complex128-multiseed`):** Reframe the **"Near-exact counts"** column to **"Near-exact min/median/max"** (just like we do for loss).
    *   *Example (100-seed complex128):*
        *   $n=3$: `0.0 / 3.0 / 3.0`
        *   $n=4$: `0.0 / 3.0 / 3.0`
        *   $n=5$: `0.0 / 0.0 / 0.0`
        *   $n=6$: `0.0 / 0.0 / 0.0`
*   **Table 2 (`tab:precision-comparison`):** Apply the same **"Near-exact min/median/max"** column structure.

## 2. Text Revisions (Statistical Statements)
We will update the text of the paper to reflect the 100-seed results:
*   **Section 5 (Methodology):** Update the text to state that the multi-seed campaigns run 100 independent random seeds on ATU's JANUS HPC cluster.
*   **Section 6.2 (Campaign Results):** Discuss the statistical distribution of the 100 runs.
    *   *Example:* For $n=3$, note that although the median run finds a complete set of 3 near-exact MUB pairs (loss $\approx 10^{-30}$), some seeds get stuck in local minima (loss min/median/max $\approx 10^{-30} / 10^{-30} / 0.134$), illustrating the non-convex landscape and the absolute necessity of multi-seed cluster-scale campaigns.
*   **Section 6.2 (Extended 20-seed n=6 campaign):** We can remove or adjust the discussion of the "extended 20-seed campaign" because our primary campaign now already runs **100 seeds**, which is much larger and makes a separate 20-seed campaign discussion redundant! We can merge this or reframe it as a 100-seed baseline.

## 3. Acknowledgments Update
*   Add a sentence acknowledging ATU's JANUS HPC facility for computational resources.