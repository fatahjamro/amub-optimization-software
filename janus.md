# Outline of JANUS HPC Integration Plan

This document outlines the proposed updates and additions to leverage **ATU's JANUS HPC cluster** for the paper. It describes the software additions, changes to the manuscript, and how these changes will enhance the paper.

---

## 💻 1. Software Additions

To support running on JANUS HPC, we will add the following files to the codebase:

### 📝 `scripts/submit_janus.sh` [NEW]
A standard SLURM batch script configured for the JANUS environment:
*   Requests a single node (GPU or high-performance CPU partition).
*   Allocates appropriate memory and runtime limits.
*   Loads necessary system modules and activates the python/conda environment.
*   Runs the multi-seed campaign or sweep command.

### 📝 `configs/multiseed_janus_100.yaml` [NEW]
An HPC-focused configuration file:
*   Scales the seed count from 5 to **100 seeds** for $d=6$ to explore the landscape with high statistical rigor.
*   Uses `complex128` reference precision.

---

## 📄 2. Proposed Manuscript Revisions (`d6mubOptimization.tex`)

By running on JANUS, we can update the following sections in the paper to highlight the HPC capabilities:

### Section 4: Software Workflow (SLURM Integration)
*   **Add Section:** Mention the inclusion of SLURM batch job scripts (`scripts/submit_janus.sh`) enabling native, out-of-the-box integration with high-performance computing schedulers. This highlights the portability of the software to server environments.

### Section 5: Experimental Methodology (High-Throughput Campaign)
*   **Update Campaign Description:** Reframe the $d=6, n=6$ campaign from a local laptop sweep (5 seeds) to a high-throughput cluster campaign (**100 seeds** run on JANUS HPC).

### Section 6: Results (Statistical Rigor)
*   **Update Results text & figures:** 
    *   Update Figure 3 (Loss Summary) and Figure 4 (Near-Exact Pair Counts) with data from the 100-seed campaign.
    *   Discuss the probability of finding the global minimum (e.g., *"Out of 100 random seeds, only X% successfully converged to the global minimum, confirming the necessity of cluster-scale multi-seed searches."*).

### Acknowledgments Section
*   **Add HPC Credit:** Acknowledge ATU's JANUS HPC platform for providing computational resources:
    ```latex
    We acknowledge the Atlantic Technological University (ATU) JANUS High-Performance Computing (HPC) facility for providing the computational resources and support that enabled the large-scale simulation campaigns reported in this work.
    ```

---

## 🚀 3. Proposed Execution Steps (Low-Work for You)

1.  **I create the scripts:** I will write the new SLURM script `submit_janus.sh` and YAML configuration file.
2.  **You submit the job on JANUS:** You SSH into JANUS, clone the repo, and run:
    ```bash
    sbatch scripts/submit_janus.sh
    ```
3.  **We update the paper:** Once the run completes, we copy the summary file back, regenerate the figures, and update the text in the paper.
