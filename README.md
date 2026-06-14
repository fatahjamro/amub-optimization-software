# A Reproducible Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six

This repository accompanies the manuscript:

**A Reproducible Software Workflow for Unanchored Approximate MUB Optimization: A Dimension-Six Case Study**

Authors: Abdul Fatah, Ian McLoughlin, and Saim Ghafoor

- GitHub repository: https://github.com/fatahjamro/amub-optimization-software
- Archived software DOI: **[insert Zenodo DOI after release]**
- Manuscript / arXiv: **[insert arXiv link after posting]**
- Data archive DOI, if separate: **[insert data DOI if applicable]**

---

## Overview

This repository implements a reproducible, parameter-driven workflow for optimizing approximate mutually unbiased basis configurations. Candidate bases are represented through a Lie-algebra unitary parameterization,

$$
U_k = \exp(iH_k),
$$

where \(H_k\) is Hermitian. The workflow optimizes all candidate bases simultaneously in an unanchored formulation, records pairwise AMUB defects, and exports machine-readable artifacts for reproducibility.

The main numerical case study is dimension $d=6$. The repository includes:

- single-seed validation sweep over $n=2,\ldots,7$;
- 100-seed $\texttt{complex128}$ and $\texttt{complex64}$ campaigns over $n=3,4,5,6;$
- precision-comparison summaries;
- CPU/GPU hardware benchmark scripts;
- Taylor-series matrix-exponential compatibility layer for accelerator execution;
- QPU verification analysis for a representative $d=6,n=4$ configuration;
- scripts for regenerating summary tables and figures;
- artifact-based saved results and metadata.

The numerical results should be interpreted as reproducible evidence about the optimization landscape sampled by this workflow. They do **not** constitute a proof of existence or nonexistence of complete MUB sets in dimension six.

---

## Quick Navigation for Reviewers

| Question | File or folder |
|---|---|
| What does the software do? | `DESIGN.md` |
| How do I install and run it? | `README.md`, `REPRODUCIBILITY.md` |
| How are experiments organized? | `EXPERIMENTS.md` |
| What files are saved per run? | `ARTIFACTS.md` |
| Where is the AMUB model implemented? | `src/amub/model.py` |
| Where is the AMUB loss implemented? | `src/amub/loss.py` |
| Where are diagnostics implemented? | `src/amub/diagnostics.py` |
| Where is Taylor matrix exponentiation implemented? | `src/amub/taylor_exp.py` |
| Where are experiment configs? | `configs/` |
| Where are summary tables? | `results/summaries/` |
| Where are paper figures? | `results/figures/` |
| Where are QPU verification artifacts? | `results/runs/d6_n4_complex128_seed3/quantum_results/` |
| How were JANUS/HPC jobs submitted? | `scripts/submit_janus*.sh` |

---

## Repository Structure

```text
amub-optimization-software/
│
├── README.md
├── DESIGN.md
├── REPRODUCIBILITY.md
├── ARTIFACTS.md
├── EXPERIMENTS.md
├── PAPER_TABLES.md
├── LICENSE
├── CITATION.cff
├── .zenodo.json
├── requirements.txt
├── environment.yml
├── reproduce_quick.sh
├── reproduce.sh
│
├── configs/
│   ├── single_seed_sweep.yaml
│   ├── multiseed_janus_100.yaml
│   ├── multiseed_janus_64.yaml
│   ├── multiseed_local_5seed_complex128.yaml
│   ├── multiseed_local_5seed_complex64.yaml
│   └── hardware_benchmarks.yaml
│
├── src/
│   └── amub/
│       ├── __init__.py
│       ├── model.py
│       ├── loss.py
│       ├── diagnostics.py
│       ├── taylor_exp.py
│       ├── experiment.py
│       ├── io_utils.py
│       ├── config.py
│       └── plotting.py
│
├── scripts/
│   ├── run_single_seed_sweep.py
│   ├── run_multiseed_campaign.py
│   ├── run_hardware_benchmarks.py
│   ├── summarize_results.py
│   ├── generate_figures.py
│   ├── submit_janus.sh
│   ├── submit_janus_64.sh
│   ├── submit_janus_benchmark.sh
│   ├── submit_janus_100_array.sh
│   ├── submit_janus_64_array.sh
│   └── qpu/
│       ├── build_embedded_unitaries.py
│       ├── transpile_qpu_circuits.py
│       ├── run_quantum_verification.py
│       ├── analyze_qpu_counts.py
│       └── generate_qpu_figure.py
│
├── tests/
│   ├── test_model_unitarity.py
│   ├── test_loss.py
│   ├── test_diagnostics.py
│   ├── test_taylor_exp.py
│   ├── test_artifact_io.py
│   ├── test_artifact_consistency.py
│   ├── test_reproduce_quick.py
│   └── test_qpu_postselection.py
│
├── results/
│   ├── summaries/
│   │   ├── precision_comparison_summary.csv
│   │   ├── hardware_benchmark_summary.csv
│   │   └── representative_runs_for_heatmaps.json
│   │
│   ├── figures/
│   │   ├── loss_summary_by_n_precision.pdf
│   │   ├── near_exact_pair_summary_by_n_precision.pdf
│   │   ├── pairwise_loss_spectra_complex128.pdf
│   │   └── pairwise_loss_spectra_complex64.pdf
│   │
│   └── runs/
│       └── d6_n4_complex128_seed3/
│           └── quantum_results/
│               ├── quantum_job_metadata.json
│               ├── qpu_results.json
│               ├── simulated_results.json
│               ├── compare_classical_vs_qpu.png
│               └── compare_classical_vs_sim.png
│
└── manuscript/
    ├── main.tex
    ├── references.bib
    ├── figures/
    └── compiled/
│
└── reproduce_quick.sh
└── reproduce.sh    
```
---
## License

The software code in this repository is licensed under the Apache License 2.0.

The data artifacts, summary CSV/JSON files, and figures are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0), unless otherwise stated.

SPDX identifiers:

- Code: `Apache-2.0`
- Data/figures/documentation: `CC-BY-4.0`