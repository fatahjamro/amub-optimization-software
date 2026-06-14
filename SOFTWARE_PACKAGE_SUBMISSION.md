# SOFTWARE_PACKAGE_SUBMISSION.md

# Software Package Submission Guide for `d6mubOptimization-v2`

**Project:** `d6mubOptimization-v2`  
**Manuscript target:** *Quantum*  
**Purpose:** Prepare the AMUB optimization software package, data artifacts, QPU verification files, and reproducibility documentation for journal review, GitHub release, and Zenodo archival DOI.

---

## 1. Submission Strategy

For a software-oriented journal submission, the package should be easy for reviewers to inspect, run, cite, and verify. The recommended structure is to separate the submission into three layers:

1. **Main software repository**  
   Contains source code, configurations, tests, documentation, scripts, summary results, small figure artifacts, and QPU metadata.

2. **Data supplement or separate Zenodo data record**  
   Contains large raw run directories, raw QPU counts, post-selected QPU counts, large benchmark logs, and any large generated artifacts that are too heavy for GitHub.

3. **Manuscript supplementary material**  
   Contains concise reproduction instructions, artifact maps, table-to-file mapping, and QPU metadata summaries.

This split keeps the GitHub repository lightweight and reviewable while preserving full reproducibility through a separate data archive if required.

---

## 2. Recommended Top-Level Repository Structure

Use a reviewer-friendly layout such as:

```text
d6mubOptimization-v2/
│
├── README.md
├── DESIGN.md
├── REPRODUCIBILITY.md
├── ARTIFACTS.md
├── EXPERIMENTS.md
├── PAPER_TABLES.md
├── SOFTWARE_PACKAGE_SUBMISSION.md
├── LICENSE
├── CITATION.cff
├── .zenodo.json
├── requirements.txt
├── environment.yml
├── .gitignore
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
│       ├── taylor_exp.py
│       ├── diagnostics.py
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
│   └── qpu_verification/
│       ├── qpu_job_metadata.json
│       ├── qpu_pairwise_losses.csv
│       ├── transpilation_summary.csv
│       └── figures/
│           └── compare_classical_vs_qpu.pdf
│
└── manuscript/
    ├── main.tex
    ├── references.bib
    ├── figures/
    └── compiled/
```

---

## 3. Files to Include in the Main Software Package

### 3.1 Environment and Setup Files

Include:

```text
README.md
REPRODUCIBILITY.md
DESIGN.md
ARTIFACTS.md
EXPERIMENTS.md
PAPER_TABLES.md
SOFTWARE_PACKAGE_SUBMISSION.md
requirements.txt
environment.yml
LICENSE
CITATION.cff
.zenodo.json
.gitignore
```

Purpose of each file:

- `README.md`: high-level overview, installation, quickstart, repository map, and links to manuscript artifacts.
- `REPRODUCIBILITY.md`: exact commands for tests, smoke runs, full campaigns, benchmarks, figure regeneration, and HPC execution.
- `DESIGN.md`: software architecture and mathematical-software design.
- `ARTIFACTS.md`: explanation of saved run artifacts and QPU verification artifacts.
- `EXPERIMENTS.md`: explanation of validation sweeps, 100-seed campaigns, precision campaigns, hardware benchmarks, and QPU verification.
- `PAPER_TABLES.md`: maps each manuscript table and figure to the source CSV/JSON artifact.
- `SOFTWARE_PACKAGE_SUBMISSION.md`: package checklist and release plan.
- `requirements.txt`: pip dependency list.
- `environment.yml`: conda environment definition.
- `LICENSE`: open-source license.
- `CITATION.cff`: citation metadata for GitHub and software users.
- `.zenodo.json`: metadata for Zenodo archival.
- `.gitignore`: excludes temporary files, virtual environments, credentials, logs, and large raw outputs.

---

### 3.2 Core Software Package: `src/amub/`

Include:

```text
src/amub/__init__.py
src/amub/model.py
src/amub/loss.py
src/amub/taylor_exp.py
src/amub/diagnostics.py
src/amub/experiment.py
src/amub/io_utils.py
src/amub/config.py
src/amub/plotting.py
```

Expected roles:

- `model.py`: implements `UnanchoredAMUBModel` with Lie-algebra unitary parameterization.
- `loss.py`: implements entrywise squared modulus, pairwise overlap, pairwise AMUB loss, and total Frobenius defect loss.
- `taylor_exp.py`: implements the Taylor-series matrix exponential compatibility layer.
- `diagnostics.py`: computes pairwise diagnostics, unitarity residuals, generator spectral norms, and near-exact classifications.
- `experiment.py`: orchestrates single-run optimization, best-basis tracking, diagnostics, metadata generation, and logging.
- `io_utils.py`: saves and reloads artifacts such as `.npy`, `.npz`, `.json`, and `.csv` files.
- `config.py`: loads YAML configuration files.
- `plotting.py`: figure-generation helpers, if used.

#### Required consistency checks before release

Before release, verify:

1. `loss.py` matches the equations in the manuscript.
2. `diagnostics.py` uses the same near-exact convention as the manuscript. Prefer:

```python
return bool(delta_ij <= tau)
```

3. `experiment.py` saves `best_bases` and `best_loss` from the same optimizer iterate.
4. Taylor order is either configurable or explicitly documented.
5. If Taylor backend is used, `taylor_order` is recorded in run metadata.

---

### 3.3 Execution and Analysis Scripts

Include:

```text
scripts/run_single_seed_sweep.py
scripts/run_multiseed_campaign.py
scripts/run_hardware_benchmarks.py
scripts/summarize_results.py
scripts/generate_figures.py
```

Purpose:

- `run_single_seed_sweep.py`: runs the validation sweep over candidate basis counts.
- `run_multiseed_campaign.py`: runs multi-seed structural and precision campaigns.
- `run_hardware_benchmarks.py`: benchmarks CPU/native and accelerator/Taylor pathways.
- `summarize_results.py`: aggregates run artifacts into campaign summaries.
- `generate_figures.py`: regenerates paper figures from saved summaries and diagnostics.

---

### 3.4 QPU Verification Scripts

For the IBM Quantum hardware verification, use a dedicated script folder:

```text
scripts/qpu/
```

Recommended files:

```text
scripts/qpu/build_embedded_unitaries.py
scripts/qpu/transpile_qpu_circuits.py
scripts/qpu/run_quantum_verification.py
scripts/qpu/analyze_qpu_counts.py
scripts/qpu/generate_qpu_figure.py
```

Recommended separation:

1. `build_embedded_unitaries.py`  
   Loads optimized classical bases and constructs embedded three-qubit unitaries
   \[
   V_{ij}=W_{ij}\oplus I_{2\times2}.
   \]

2. `transpile_qpu_circuits.py`  
   Builds and transpiles Qiskit circuits using the chosen backend and optimization level.

3. `run_quantum_verification.py`  
   Runs circuits on IBM Quantum hardware when credentials and access are available.

4. `analyze_qpu_counts.py`  
   Recomputes QPU transition matrices and pairwise losses from saved raw counts.

5. `generate_qpu_figure.py`  
   Regenerates `compare_classical_vs_qpu` figure from saved QPU CSV files.

This separation is important because reviewers may not have access to the same IBM backend. They should still be able to reproduce the QPU analysis from saved counts and metadata.

---

### 3.5 Configuration Files: `configs/`

Include the main reported configurations:

```text
configs/single_seed_sweep.yaml
configs/multiseed_janus_100.yaml
configs/multiseed_janus_64.yaml
configs/hardware_benchmarks.yaml
```

Also include local development configurations, but name them clearly:

```text
configs/multiseed_local_5seed_complex128.yaml
configs/multiseed_local_5seed_complex64.yaml
```

Do not leave five-seed local configs with names that imply they are the full 100-seed campaigns.

---

### 3.6 Automated Testing Suite: `tests/`

Include tests for mathematical correctness, artifact integrity, and QPU post-selection.

Recommended files:

```text
tests/test_model_unitarity.py
tests/test_loss.py
tests/test_diagnostics.py
tests/test_taylor_exp.py
tests/test_artifact_io.py
tests/test_artifact_consistency.py
tests/test_reproduce_quick.py
tests/test_qpu_postselection.py
```

Recommended tests:

1. **Model unitarity test**  
   Verify that generated bases satisfy small Frobenius unitarity residuals.

2. **Loss test**  
   Verify that known or saved near-exact configurations give near-zero pairwise AMUB loss.

3. **Diagnostics test**  
   Verify that near-exact counts are recomputed correctly from `pairwise_diagnostics.json`.

4. **Taylor comparison test**  
   Compare `taylor_matrix_exp` against `torch.matrix_exp` for small test matrices.

5. **Artifact consistency test**  
   Load `best_bases.npy`, recompute total AMUB loss, and compare with `run_metadata.json["best_loss"]`.

6. **QPU post-selection test**  
   Verify that counts for states `0,...,5` are retained, states `6,7` are discarded, and the retained counts are renormalized correctly.

---

### 3.7 Pipeline Automation

Include:

```text
reproduce_quick.sh
reproduce.sh
scripts/submit_janus.sh
scripts/submit_janus_64.sh
scripts/submit_janus_benchmark.sh
scripts/submit_janus_100_array.sh
scripts/submit_janus_64_array.sh
```

Guidelines:

- `reproduce_quick.sh` should run tests and a lightweight smoke-test campaign.
- `reproduce.sh` should reproduce the main configured workflows, or document expected runtime clearly.
- SLURM scripts should activate the environment, run the same Python entry points as local execution, and write logs/artifacts to predictable folders.
- Array scripts should be documented as optional seed-parallel reproduction scripts unless they generated the reported manuscript data.
- Check shell scripts for syntax errors before release.

---

## 4. Results and Data Packaging

### 4.1 Include Small Summary Results in GitHub

Keep the following files in the repository:

```text
results/summaries/precision_comparison_summary.csv
results/summaries/hardware_benchmark_summary.csv
results/summaries/representative_runs_for_heatmaps.json
results/figures/
results/qpu_verification/qpu_job_metadata.json
results/qpu_verification/qpu_pairwise_losses.csv
results/qpu_verification/transpilation_summary.csv
results/qpu_verification/figures/compare_classical_vs_qpu.pdf
```

These files are small, directly support manuscript tables and figures, and help reviewers verify the paper without rerunning expensive campaigns.

---

### 4.2 Archive Large Raw Artifacts Separately

Do not include very large raw outputs in the main GitHub repository. Archive them separately on Zenodo or another data repository.

Archive separately if large:

```text
results/runs/
results/qpu_verification/qpu_counts_raw/
results/qpu_verification/qpu_counts_postselected/
results/benchmarks/raw_benchmarks.json
large logs
full benchmark traces
```

If a file is small and directly needed for manuscript verification, it may stay in GitHub. If it is large, move it to a data supplement and link it from `README.md`, `ARTIFACTS.md`, and the manuscript Code/Data Availability section.

---

## 5. QPU Verification Artifacts

Create:

```text
results/qpu_verification/
```

Recommended contents:

```text
results/qpu_verification/qpu_job_metadata.json
results/qpu_verification/qpu_pairwise_losses.csv
results/qpu_verification/transpilation_summary.csv
results/qpu_verification/qpu_counts_raw/
results/qpu_verification/qpu_counts_postselected/
results/qpu_verification/figures/compare_classical_vs_qpu.pdf
```

### 5.1 Recommended `qpu_job_metadata.json`

```json
{
  "backend": "ibm_marrakesh",
  "processor": "Heron r2",
  "num_qubits": 156,
  "shots": 2000,
  "qiskit_version": "...",
  "qiskit_ibm_runtime_version": "...",
  "optimization_level": 1,
  "job_ids": ["..."],
  "run_date_utc": "...",
  "basis_pairs": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],
  "postselection": {
    "active_states": [0,1,2,3,4,5],
    "discarded_states": [6,7]
  },
  "num_circuits": 36,
  "inputs_per_pair": 6,
  "embedding": "V_ij = W_ij direct_sum I_2",
  "measurement_mitigation": false,
  "postselection_normalization": "renormalize over active states 0,...,5"
}
```

### 5.2 QPU Security Warning

Never commit:

```text
.env
IBM API tokens
IBM Cloud CRNs
account credentials
private backend access credentials
```

Use environment variables or local `.env` files that are excluded by `.gitignore`.

---

## 6. Recommended `.gitignore`

Use a `.gitignore` similar to:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/

# Environments
venv/
.env
*.env
.venv/
conda-meta/

# OS files
.DS_Store

# Logs
*.log
*.err
results/logs/

# Large raw outputs
results/runs/
results/qpu_verification/qpu_counts_raw/
results/qpu_verification/qpu_counts_postselected/

# Keep summaries and figures
!results/summaries/
!results/summaries/*.csv
!results/summaries/*.json
!results/figures/
!results/figures/*
!results/qpu_verification/qpu_job_metadata.json
!results/qpu_verification/qpu_pairwise_losses.csv
!results/qpu_verification/transpilation_summary.csv
!results/qpu_verification/figures/
!results/qpu_verification/figures/*
```

---

## 7. `CITATION.cff` Template

Create a top-level `CITATION.cff` file:

```yaml
cff-version: 1.2.0
title: "d6mubOptimization-v2: Reproducible AMUB Optimization Workflow"
message: "If you use this software, please cite it using the metadata from this file."
type: software
authors:
  - family-names: "Fatah"
    given-names: "Abdul"
  - family-names: "McLoughlin"
    given-names: "Ian"
  - family-names: "Ghafoor"
    given-names: "Saim"
repository-code: "https://github.com/fatahjamro/d6mubOptimization-v2"
version: "1.0.0"
date-released: "2026-06-14"
license: "MIT"
```

Change the license if the project uses a different license.

---

## 8. `.zenodo.json` Template

Create a top-level `.zenodo.json` file:

```json
{
  "title": "d6mubOptimization-v2: Reproducible AMUB Optimization Workflow",
  "upload_type": "software",
  "description": "A reproducible Python/PyTorch workflow for unanchored approximate mutually unbiased basis optimization, including dimension-six multi-seed campaigns, precision comparison, hardware benchmarks, and QPU verification analysis.",
  "creators": [
    {
      "name": "Fatah, Abdul"
    },
    {
      "name": "McLoughlin, Ian"
    },
    {
      "name": "Ghafoor, Saim"
    }
  ],
  "access_right": "open",
  "license": "MIT",
  "keywords": [
    "mutually unbiased bases",
    "quantum information",
    "approximate MUB",
    "PyTorch",
    "mathematical software",
    "reproducibility",
    "quantum hardware"
  ],
  "version": "1.0.0"
}
```

---

## 9. Zenodo Release Workflow

Use this workflow after the repository is clean and tested.

### 9.1 Local checks

```bash
git status
pytest tests/
./reproduce_quick.sh
```

### 9.2 Commit and tag

```bash
git add .
git commit -m "Prepare reproducible AMUB workflow release"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

### 9.3 Create GitHub release

On GitHub:

1. Open the repository.
2. Go to **Releases**.
3. Click **Draft a new release**.
4. Select tag `v1.0.0`.
5. Add release title:

```text
d6mubOptimization-v2 v1.0.0
```

6. Add release notes summarizing:
   - AMUB workflow;
   - dimension-six campaigns;
   - precision comparison;
   - hardware benchmarks;
   - QPU verification artifacts;
   - DOI pending from Zenodo.

### 9.4 Zenodo DOI

After Zenodo processes the GitHub release, copy the DOI into:

```text
README.md
CITATION.cff
manuscript Code/Data Availability section
```

---

## 10. Recommended README Reviewer Navigation

At the top of `README.md`, include:

```markdown
# d6mubOptimization-v2

Reproducible software workflow for unanchored approximate mutually unbiased basis optimization.

This repository accompanies the manuscript:

**A Generalized Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six**

## Quick Navigation

| Reviewer question | Where to look |
|---|---|
| What does the software do? | `DESIGN.md` |
| How do I install it? | `README.md` → Installation |
| How do I run a quick test? | `./reproduce_quick.sh` |
| How do I reproduce the full campaigns? | `./reproduce.sh` |
| Where is the model implemented? | `src/amub/model.py` |
| Where is the AMUB loss implemented? | `src/amub/loss.py` |
| Where are diagnostics computed? | `src/amub/diagnostics.py` |
| Where is Taylor matrix exponential implemented? | `src/amub/taylor_exp.py` |
| Where are campaign configs? | `configs/` |
| Where are saved summary tables? | `results/summaries/` |
| Where are QPU verification artifacts? | `results/qpu_verification/` |
| How were JANUS runs submitted? | `scripts/submit_janus*.sh` |
```

---

## 11. `PAPER_TABLES.md` Template

Create:

```markdown
# PAPER_TABLES.md

This file maps manuscript tables and figures to the source data artifacts.

## Single-seed sweep table

Source:

```text
results/summaries/single_seed_sweep_summary.csv
```

## Multi-seed complex128 campaign table

Source:

```text
results/summaries/precision_comparison_summary.csv
```

Rows:

```text
dtype == complex128
```

## Precision comparison table

Source:

```text
results/summaries/precision_comparison_summary.csv
```

## Hardware benchmark table

Source:

```text
results/summaries/hardware_benchmark_summary.csv
```

## Representative heatmaps and spectra

Source:

```text
results/summaries/representative_runs_for_heatmaps.json
```

## QPU verification figure

Sources:

```text
results/qpu_verification/qpu_pairwise_losses.csv
results/qpu_verification/qpu_job_metadata.json
results/qpu_verification/transpilation_summary.csv
```
```

---

## 12. Manuscript Code and Data Availability Statement

Use a statement like:

```latex
\section*{Code and Data Availability}

The source code, configuration files, reproduction scripts, and summary artifacts for the AMUB workflow are available at \url{https://github.com/fatahjamro/d6mubOptimization-v2}. The archived software release is available on Zenodo at DOI: \texttt{[insert DOI]}. The repository includes the Lie-exponential AMUB model, loss functions, diagnostics, Taylor matrix-exponential compatibility layer, campaign runners, hardware benchmark scripts, QPU verification scripts, and figure-generation utilities. Summary CSV/JSON files used to generate the manuscript tables and figures are stored in \texttt{results/summaries/}. QPU verification metadata and pairwise-loss summaries are stored in \texttt{results/qpu\_verification/}. Large raw run artifacts and QPU count data are archived separately at DOI: \texttt{[insert data DOI]}, when not included directly in the GitHub repository.
```

---

## 13. Final Release Checklist

Before journal submission, verify:

- [ ] `pytest tests/` passes.
- [ ] `./reproduce_quick.sh` passes from a clean environment.
- [ ] `README.md` includes installation, quickstart, and reviewer navigation.
- [ ] `DESIGN.md` describes architecture accurately.
- [ ] `REPRODUCIBILITY.md` gives exact commands.
- [ ] `ARTIFACTS.md` explains all saved files.
- [ ] `EXPERIMENTS.md` explains single-seed, multi-seed, precision, benchmark, and QPU experiments.
- [ ] `PAPER_TABLES.md` maps each table/figure to CSV/JSON source files.
- [ ] Full 100-seed configs are clearly distinguished from local five-seed configs.
- [ ] `best_loss` matches recomputed loss from `best_bases.npy` in artifact consistency tests.
- [ ] Near-exact classification convention matches manuscript equations.
- [ ] Metadata records backend, device, dtype, matrix-exponential pathway, and Taylor order when applicable.
- [ ] QPU metadata includes backend, processor, shots, job IDs, Qiskit versions, post-selection rule, and run date.
- [ ] No credentials, `.env` files, IBM API tokens, or CRNs are committed.
- [ ] SLURM scripts have been syntax-checked.
- [ ] Optional array scripts are documented as optional or clearly identified as the scripts used for reported runs.
- [ ] Summary CSV/JSON files are generated from saved artifacts, not manually edited.
- [ ] Hardware benchmark methodology is documented.
- [ ] Repository has `LICENSE`, `CITATION.cff`, and `.zenodo.json`.
- [ ] GitHub release tag is created, e.g. `v1.0.0`.
- [ ] Zenodo DOI is added to README and manuscript.
- [ ] Large raw data are archived separately if not included in GitHub.

---

## 14. Short Recommendation

For the journal submission, package the GitHub repository as the main software artifact and archive a versioned release on Zenodo to obtain a DOI. Keep the repository lightweight by including source code, configs, tests, documentation, summary CSV/JSON files, figures, and QPU metadata. Archive large raw run directories and raw QPU counts as a separate data supplement. This structure allows reviewers to inspect the software quickly, reproduce small tests immediately, regenerate figures from saved summaries, and access full raw artifacts when needed.
