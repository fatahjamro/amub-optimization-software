# REPRODUCIBILITY.md

# Reproducibility Guide for `amub-optimization-software`

This guide provides instructions to reproduce the numerical and hardware benchmarking results reported in the manuscript.

---

## 1. Installation & Environment Setup

We recommend using a clean virtual environment or a conda environment.

### Option A: Python Virtual Environment (pip)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option B: Conda Environment
```bash
conda env create -f environment.yml
conda activate d6mub-optimization
```

---

## 2. Automated Correctness Tests

Verify that mathematical properties (unitarity, losses, Taylor matrix exponential fallback, diagnostics) behave correctly by running the pytest suite:
```bash
pytest tests/
```

---

## 3. Smoke-Test Pipeline

For a fast end-to-end check of the optimization, summarization, and figure generation scripts, run the provided shell script:
```bash
./reproduce_quick.sh
```
This runs a small 3-basis and 4-basis optimization over 50 steps, aggregates the outcomes, and generates preview plots in under 2 seconds.

---

## 4. Full Paper Campaigns

To execute the local campaigns (sweeping bases $n = 3, \ldots, 6$ with seeds $0, \ldots, 4$ for precision campaigns, and seeds $0, \ldots, 19$ for the $n=6$ campaign) and generate the summary artifacts, run the local reproduction script:
```bash
./reproduce.sh
```
*Note:* This script will run the full set of configured optimization sweeps and regenerate all publication-quality vector plots in the `results/` directory.

---

## 5. Hardware Performance Benchmarks

To benchmark optimization speed and reproduce the execution scaling crossover (CPU vs. GPU) across dimensions $d \in \{6, 12, 24, 48, 96\}$, run:
```bash
python3 scripts/run_hardware_benchmarks.py
```
This automatically routes the matrix exponentiation to the custom Taylor-series layer on active GPU backends (`mps` or `cuda`) and falls back to native double-precision matrix exp on CPU.

---

## 6. High-Performance Computing (HPC) Execution

To reproduce the full 100-seed campaigns (seeds $0, \dots, 99$) on a SLURM-managed HPC cluster (like the ATU JANUS facility), submit the provided array and benchmark scripts:

*   **Double-Precision Campaign (100 Seeds):**
    ```bash
    sbatch scripts/submit_janus_100_array.sh
    ```
*   **Single-Precision Campaign (100 Seeds):**
    ```bash
    sbatch scripts/submit_janus_64_array.sh
    ```
*   **Hardware Benchmark Suite:**
    ```bash
    sbatch scripts/submit_janus_benchmark.sh
    ```

---

## 7. Quantum Hardware Verification

The physical hardware verification on IBM Quantum devices is managed by `scripts/qpu/run_quantum_verification.py`. It has three execution modes:

1.  **Local Simulation Dry-Run:**
    ```bash
    python3 scripts/qpu/run_quantum_verification.py --run_dir results/runs/d6_n4_complex128_seed3 --mode sim
    ```
2.  **Job Submission to IBM Quantum (Requires API Token):**
    ```bash
    python3 scripts/qpu/run_quantum_verification.py --run_dir results/runs/d6_n4_complex128_seed3 --mode submit --backend ibm_marrakesh
    ```
3.  **Job Retrieval and Post-Processing:**
    ```bash
    python3 scripts/qpu/run_quantum_verification.py --run_dir results/runs/d6_n4_complex128_seed3 --mode retrieve
    ```
    Once the IBM Quantum job is complete, this pulls the raw counts, applies post-selection (discarding states $|6\rangle$ and $|7\rangle$), and generates the comparison plot `compare_classical_vs_qpu.png`.
