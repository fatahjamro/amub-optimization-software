# ARTIFACTS.md

# Software Artifacts in `d6mubOptimization-v2`

This document details the file schema and output organization of the saved optimization runs and QPU verification experiments.

---

## 1. Classical Run Directories

Every completed run produces a subfolder named according to the configuration (e.g., `results/runs/d6_n4_complex128_seed3/`). Within each run folder, the following files are written:

1.  **`best_bases.npy`** (Binary NumPy matrix)
    *   *Shape:* `(n, d, d)` where $n$ is the number of bases and $d$ is the dimension.
    *   *Type:* Complex matrix (`complex128` or `complex64`).
    *   *Description:* The collection of optimized basis unitary matrices $U_0, \ldots, U_{n-1}$ that yielded the lowest loss during optimization.
2.  **`pairwise_overlaps.npz`** (NumPy compressed archive)
    *   *Key:* `overlaps`
    *   *Shape:* `(n, n, d, d)`
    *   *Description:* The transition matrices $M_{ij} = |U_i^\dagger U_j|^2$ for all pairs.
3.  **`pairwise_diagnostics.json`** (JSON)
    *   *Format:* A list of dictionaries, one per pair $(i, j)$ with $i < j$.
    *   *Schema:*
        ```json
        [
          {
            "pair": [0, 1],
            "loss": 0.05555555555555555,
            "max_absolute_deviation": 0.16666666666666666,
            "near_exact_1e-06": false,
            "near_exact_1e-08": false
          }
        ]
        ```
4.  **`unitarity_residuals.json`** (JSON)
    *   *Format:* Dictionary mapping basis index to Frobenius residual value.
    *   *Schema:*
        ```json
        {
          "basis_0": 1.28e-15,
          "basis_1": 1.41e-15
        }
        ```
5.  **`generator_norms.json`** (JSON)
    *   *Format:* Dictionary mapping basis index to Frobenius norm of the generator $H_k$.
    *   *Schema:*
        ```json
        {
          "basis_0": 0.8123,
          "basis_1": 0.9412
        }
        ```
6.  **`optimization_history.csv`** (CSV)
    *   *Columns:* `step`, `loss`, `lr`
    *   *Description:* Log of loss and learning rate at each checkpoint.
7.  **`run_metadata.json`** (JSON)
    *   *Description:* Comprehensive metadata containing final step counts, device backend, precision datatypes, best loss values, time taken, and system info.

---

## 2. QPU Verification Artifacts

The QPU verification output is stored under a run's `quantum_results/` subdirectory:

1.  **`quantum_job_metadata.json`** (JSON)
    *   *Schema:*
        ```json
        {
          "job_id": "d8n2oo3nn5bs738u1qgg",
          "backend": "ibm_marrakesh",
          "shots": 2000,
          "run_dir": "/Users/fatah/Documents/d6mubOptimization-v2/results/runs/d6_n4_complex128_seed3",
          "metadata": [
            {"pair": [0, 1], "input_state": 0},
            ...
          ]
        }
        ```
2.  **`simulated_results.json`** (JSON)
    *   *Description:* Ideal transition matrices and pairwise losses calculated via local Qiskit simulation sampler.
3.  **`qpu_results.json`** (JSON)
    *   *Description:* Physical hardware transition matrices and pairwise losses reconstructed from post-selected experimental QPU counts.
4.  **`compare_classical_vs_sim.png`** (PNG)
    *   *Description:* Defect spectrum comparing ideal classical losses to Qiskit simulation results.
5.  **`compare_classical_vs_qpu.png`** (PNG)
    *   *Description:* Defect spectrum comparing ideal classical losses to physical QPU measurement outcomes.
