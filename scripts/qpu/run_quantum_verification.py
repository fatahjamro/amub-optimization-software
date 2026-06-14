#!/usr/bin/env python3
"""
Quantum Hardware Verification Script for Unanchored AMUB (d=6, n=4)
Supports:
1. Local simulation dry run (mode: sim)
2. IBM Quantum job submission (mode: submit)
3. IBM Quantum job retrieval, post-selection, and analysis (mode: retrieve)
"""

import argparse
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Qiskit imports
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate
from qiskit.primitives import StatevectorSampler


def get_input_state_circuit(k: int) -> QuantumCircuit:
    """
    Create a 3-qubit circuit and prepare the computational basis state |k>.
    Input k is in range 0 to 5.
    Qiskit ordering: qubit 0 is the rightmost bit (LSB), qubit 2 is the leftmost bit (MSB).
    """
    qc = QuantumCircuit(3)
    # Convert k to a 3-bit binary string (big-endian), e.g. 3 -> '011'
    binary = format(k, '03b')
    # Loop in reverse order to map LSB to qubit 0, MSB to qubit 2
    for idx, char in enumerate(reversed(binary)):
        if char == '1':
            qc.x(idx)
    return qc


def build_verification_circuits(bases: np.ndarray):
    """
    Build the 36 quantum circuits needed for d=6, n=4 verification.
    For each pair of bases (i, j) with i < j, and for each input state k in {0..5}:
    1. Compute W = U_i^H @ U_j
    2. Embed W into an 8x8 matrix V
    3. Prepare state |k>
    4. Apply V
    5. Measure all 3 qubits
    """
    circuits = []
    metadata = []
    
    n_bases = bases.shape[0]
    for i in range(n_bases):
        for j in range(i + 1, n_bases):
            # Compute W = U_i^\dagger @ U_j
            U_i = bases[i]
            U_j = bases[j]
            W = U_i.conj().T @ U_j
            
            # Embed W into 8x8 unitary V (3 qubits)
            V = np.eye(8, dtype=complex)
            V[:6, :6] = W
            
            gate = UnitaryGate(V, label=f"U_{i}_dag_U_{j}")
            
            for k in range(6):
                qc = get_input_state_circuit(k)
                qc.append(gate, [0, 1, 2])
                qc.measure_all()
                
                circuits.append(qc)
                metadata.append({
                    "pair": [i, j],
                    "input_state": k
                })
                
    return circuits, metadata


def post_process_counts(counts: dict) -> np.ndarray:
    """
    Apply post-selection to raw counts from a 3-qubit measurement.
    Discards outcomes '110' (6) and '111' (7), and normalizes the rest.
    Returns a probability vector of length 6.
    """
    probabilities = np.zeros(6)
    valid_total = 0
    
    # Read valid states 0 to 5
    for k in range(6):
        bitstr = format(k, '03b')
        count = counts.get(bitstr, 0)
        probabilities[k] = count
        valid_total += count
        
    if valid_total > 0:
        probabilities /= valid_total
    else:
        # Fallback if no counts fell in the valid subspace (unlikely)
        probabilities = np.ones(6) / 6.0
        
    return probabilities


def reconstruct_overlaps(results_counts, metadata, d=6) -> dict:
    """
    Reconstruct the 6x6 transition matrices M_ij = |U_i^\dagger U_j|^2 from counts.
    results_counts is a list of counts dicts, matching the order of metadata.
    """
    # Initialize overlap matrices for all 6 pairs
    overlaps = {}
    
    # Populate the columns of each pair's overlap matrix
    for idx, counts in enumerate(results_counts):
        meta = metadata[idx]
        pair_key = f"{meta['pair'][0]}_{meta['pair'][1]}"
        k = meta['input_state']
        
        if pair_key not in overlaps:
            overlaps[pair_key] = np.zeros((d, d))
            
        prob_col = post_process_counts(counts)
        # Entrywise squared overlap: M_{ij, a k} = | <a| U_i^\dagger U_j |k> |^2
        # Row index 'a' corresponds to measured output state, column 'k' corresponds to input state
        overlaps[pair_key][:, k] = prob_col
        
    return overlaps


def compute_pairwise_losses(overlaps, d=6) -> dict:
    """
    Compute the Frobenius norm squared defect from mutually unbiased condition for each pair:
    loss = sum( (M_ij - 1/d)^2 )
    """
    losses = {}
    target = 1.0 / d
    for pair_key, M in overlaps.items():
        loss = np.sum((M - target) ** 2)
        losses[pair_key] = float(loss)
    return losses


def plot_comparison(classical_losses: dict, experimental_losses: dict, mode_name: str, output_path: Path):
    """
    Plot a comparative pairwise-loss spectrum comparing classical (ideal) to experimental/simulated.
    """
    # Sort pairs by classical loss value
    sorted_pairs = sorted(classical_losses.keys(), key=lambda k: classical_losses[k])
    
    classical_vals = [classical_losses[k] for k in sorted_pairs]
    exp_vals = [experimental_losses[k] for k in sorted_pairs]
    
    labels = [f"Pair ({p.replace('_', ',')})" for p in sorted_pairs]
    
    x = np.arange(len(sorted_pairs))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, classical_vals, width, label='Classical (Ideal)', color='#4285F4', alpha=0.9)
    ax.bar(x + width/2, exp_vals, width, label=f'QPU ({mode_name})', color='#EA4335', alpha=0.9)
    
    ax.set_ylabel('Pairwise Loss $\ell_{ij}$')
    ax.set_title(f'AMUB Pairwise Defect Spectrum: Classical vs. {mode_name}')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    ax.legend()
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Plot saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Quantum Hardware Verification for Unanchored AMUB (d=6, n=4).")
    parser.add_argument("--run_dir", type=str, default="results/runs/d6_n4_complex128_seed3", help="Directory of the run to verify.")
    parser.add_argument("--mode", type=str, choices=["sim", "submit", "retrieve"], default="sim", help="Execution mode.")
    parser.add_argument("--backend", type=str, default=None, help="Name of IBM Quantum backend (default: least busy).")
    parser.add_argument("--shots", type=int, default=2000, help="Number of shots per circuit.")
    parser.add_argument("--job_id", type=str, default=None, help="Job ID to retrieve (retrieve mode only).")
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Error: Run directory {run_dir} does not exist.")
        sys.exit(1)
        
    bases_path = run_dir / "best_bases.npy"
    if not bases_path.exists():
        print(f"Error: best_bases.npy not found in {run_dir}.")
        sys.exit(1)
        
    # Load optimized classical bases
    print(f"Loading optimized bases from {bases_path}...")
    bases = np.load(bases_path)
    
    # Read classical pairwise losses for comparison
    classical_losses = {}
    diag_path = run_dir / "pairwise_diagnostics.json"
    if diag_path.exists():
        with open(diag_path, 'r') as f:
            diags = json.load(f)
        for d_item in diags:
            p_tuple = d_item['pair']
            classical_losses[f"{p_tuple[0]}_{p_tuple[1]}"] = d_item['loss']
    else:
        # Fallback: compute classical losses from bases directly
        print("Warning: pairwise_diagnostics.json not found. Recomputing classical losses...")
        for i in range(4):
            for j in range(i + 1, 4):
                U_i = bases[i]
                U_j = bases[j]
                overlap = np.abs(U_i.conj().T @ U_j) ** 2
                loss = np.sum((overlap - 1.0/6.0) ** 2)
                classical_losses[f"{i}_{j}"] = float(loss)
                
    # Build Qiskit verification circuits
    print("Building 36 verification circuits...")
    circuits, metadata = build_verification_circuits(bases)
    
    # Outputs directory
    out_dir = run_dir / "quantum_results"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if args.mode == "sim":
        print(f"Running locally via StatevectorSampler with {args.shots} shots...")
        sampler = StatevectorSampler()
        job = sampler.run(circuits, shots=args.shots)
        res = job.result()
        
        counts_list = []
        for idx in range(len(circuits)):
            counts_list.append(res[idx].data.meas.get_counts())
            
        # Post-select and reconstruct
        print("Post-selecting simulator results...")
        overlaps_sim = reconstruct_overlaps(counts_list, metadata)
        losses_sim = compute_pairwise_losses(overlaps_sim)
        
        # Save results
        results_json = {
            "classical_losses": classical_losses,
            "simulated_losses": losses_sim,
            "overlaps": {k: v.tolist() for k, v in overlaps_sim.items()}
        }
        with open(out_dir / "simulated_results.json", 'w') as f:
            json.dump(results_json, f, indent=4)
        print("Simulated results saved to simulated_results.json.")
        
        # Plot spectrum
        plot_comparison(classical_losses, losses_sim, "Simulator", out_dir / "compare_classical_vs_sim.png")
        
    elif args.mode == "submit":
        print("Authenticating with IBM Quantum Service...")
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        
        try:
            service = QiskitRuntimeService()
        except Exception as e:
            print(f"Error authenticating with IBM Quantum: {e}")
            sys.exit(1)
            
        # Select backend
        if args.backend:
            backend_name = args.backend
            backend = service.backend(backend_name)
        else:
            print("Finding least busy backend with at least 3 qubits...")
            backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
            backend_name = backend.name
            
        print(f"Selected QPU backend: {backend_name}")
        
        # Transpile circuits
        print("Transpiling circuits for QPU architecture (optimization_level=1)...")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuits = pm.run(circuits)
        
        # Submit job
        print(f"Submitting 36 circuits to {backend_name} with {args.shots} shots...")
        sampler = Sampler(mode=backend)
        job = sampler.run(isa_circuits, shots=args.shots)
        job_id = job.job_id()
        print(f"Job successfully submitted! Job ID: {job_id}")
        
        # Save job metadata for retrieval
        job_meta = {
            "job_id": job_id,
            "backend": backend_name,
            "shots": args.shots,
            "run_dir": str(run_dir.resolve()),
            "metadata": metadata
        }
        meta_path = out_dir / "quantum_job_metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(job_meta, f, indent=4)
        print(f"Saved job metadata to {meta_path}. Run this script in 'retrieve' mode once the job is done.")
        
    elif args.mode == "retrieve":
        # Check Job ID
        job_id = args.job_id
        meta_path = out_dir / "quantum_job_metadata.json"
        
        if not job_id and meta_path.exists():
            print(f"Reading job ID from metadata file {meta_path}...")
            with open(meta_path, 'r') as f:
                job_meta = json.load(f)
            job_id = job_meta["job_id"]
            
        if not job_id:
            print("Error: No job ID provided and no quantum_job_metadata.json found.")
            sys.exit(1)
            
        print(f"Retrieving job {job_id} from IBM Quantum Service...")
        from qiskit_ibm_runtime import QiskitRuntimeService
        try:
            service = QiskitRuntimeService()
            job = service.job(job_id)
        except Exception as e:
            print(f"Error retrieving job: {e}")
            sys.exit(1)
            
        status = job.status()
        print(f"Current job status: {status}")
        
        if status not in ["DONE", "COMPLETED"]:
            print("Job is not complete yet. Please try again later.")
            sys.exit(0)
            
        print("Fetching results from IBM cloud...")
        res = job.result()
        
        counts_list = []
        for idx in range(len(circuits)):
            # Robust extraction of counts for each circuit
            pub_res = res[idx]
            data_keys = list(pub_res.data.keys())
            if len(data_keys) > 0:
                counts = pub_res.data[data_keys[0]].get_counts()
            else:
                counts = pub_res.data.meas.get_counts()
            counts_list.append(counts)
            
        # Post-select and reconstruct
        print("Post-selecting hardware results...")
        overlaps_qpu = reconstruct_overlaps(counts_list, metadata)
        losses_qpu = compute_pairwise_losses(overlaps_qpu)
        
        # Save results
        results_json = {
            "job_id": job_id,
            "backend": job.backend().name if hasattr(job, 'backend') else "Unknown",
            "classical_losses": classical_losses,
            "qpu_losses": losses_qpu,
            "overlaps": {k: v.tolist() for k, v in overlaps_qpu.items()}
        }
        with open(out_dir / "qpu_results.json", 'w') as f:
            json.dump(results_json, f, indent=4)
        print("Physical hardware results saved to qpu_results.json.")
        
        # Plot spectrum
        plot_comparison(classical_losses, losses_qpu, "Hardware", out_dir / "compare_classical_vs_qpu.png")
        

if __name__ == "__main__":
    main()
