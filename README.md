# A Generalized Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six

This repository contains the official, fully reproducible mathematical software workflow accompanying our submission to *Quantum*: **"A Generalized Software Workflow for Unanchored Approximate MUB Optimization: A Case Study in Dimension Six"**.

It implements unanchored continuous approximate Mutually Unbiased Basis (AMUB) optimization using PyTorch automatic differentiation and includes a custom hardware-accelerated Taylor expansion layer to support Apple Silicon GPUs (MPS) and NVIDIA GPUs (CUDA).

---

## 📂 Repository Structure

*   `configs/`: Standardized campaign configurations (YAML) for single-seed sweeps, multi-seed campaigns, and benchmarks.
*   `src/amub/`: The core package library (model parameterization, losses, diagnostics, Taylor fallbacks, and vector plotting).
*   `scripts/`: Command-line tools to run sweeps, compile summaries, and generate figures.
*   `tests/`: Automated mathematical correctness test suite (`pytest`).
*   `manuscript/`: Directory containing all LaTeX draft files, BibTeX references, style files, and compiled outputs.
*   `results/`: Summary CSV files, JSON diagnostics, and paper-ready figures.
*   `reproduce_quick.sh`: Smoke test pipeline (runs tests, runs mini sweep, and exports figures in under 2 seconds).
*   `reproduce.sh`: The full campaign reproduction script.

---

## 🚀 Quick Start & Installation

### 1. Environment Setup
We recommend using either a virtual environment or conda:

#### Option A: Pip Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Option B: Conda Environment
```bash
conda env create -f environment.yml
conda activate d6mub-optimization
```

---

## ⚡ Reproducing Paper Results

### 1. Run the Automated Test Suite
To verify the custom Taylor layer limits, loss properties, and unitarity:
```bash
pytest tests/
```

### 2. Run the Smoke Test Pipeline
To run a fast, end-to-end campaign and instantly verify the figures:
```bash
./reproduce_quick.sh
```

### 3. Run the Full Campaign Reproduction
To execute the complete double and single precision multi-seed optimization campaigns (sweeping bases $n = 3, \ldots, 6$ and random seeds $0, \ldots, 99$), run:
```bash
./reproduce.sh
```

### 4. Run the Hardware Benchmarks
To reproduce the performance crossover scaling (CPU vs GPU) across matrix dimensions $d = 6, 12, 24, 48, 96$, execute:
```bash
python3 scripts/run_hardware_benchmarks.py
```
This script automatically utilizes our custom Taylor matrix exponentiation fallback on active GPU devices (`mps` or `cuda`) and falls back gracefully to CPU if no accelerator is present.

### 🖥️ 5. Run on High-Performance Computing (HPC) Clusters
To run the large-scale campaigns (100 seeds) and benchmark runs on a SLURM-managed HPC cluster like ATU's JANUS facility, submit the provided batch scripts:
*   **Double-Precision Sweep (100 seeds):**
    ```bash
    sbatch scripts/submit_janus_100_array.sh
    ```
*   **Single-Precision Sweep (100 seeds):**
    ```bash
    sbatch scripts/submit_janus_64_array.sh
    ```
*   **Hardware Benchmark:**
    ```bash
    sbatch scripts/submit_janus_benchmark.sh
    ```
These scripts automate resource allocation, environment activation, multi-seed campaigns, and timing runs on the cluster, outputting logs and results directly to the `results/` folder.
