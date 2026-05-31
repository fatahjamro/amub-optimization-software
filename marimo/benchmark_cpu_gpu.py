#!/usr/bin/env python3
import time
import torch
import json

def compute_amub_loss(bases, d):
    n = len(bases)
    loss = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            # Compute entrywise absolute squared overlap: |U_i^H U_j|^2
            overlap = torch.abs(bases[i].mH @ bases[j]) ** 2
            # Defect: Frobenius norm squared of (overlap - 1/d)
            loss += torch.sum((overlap - 1.0 / d) ** 2)
    return loss

def taylor_matrix_exp(X, order=20):
    eye = torch.eye(X.shape[-1], dtype=X.dtype, device=X.device)
    term = eye
    result = eye
    for i in range(1, order + 1):
        term = term @ X / i
        result = result + term
    return result

def run_benchmark_for_config(device_name, dtype, use_taylor, d, n_bases=6, steps=500):
    device = torch.device(device_name)
    
    # Initialize unconstrained complex matrix parameters
    params = [
        torch.nn.Parameter(torch.randn(d, d, dtype=dtype, device=device) * 0.05)
        for _ in range(n_bases)
    ]
    
    optimizer = torch.optim.Adam(params, lr=0.02)
    
    # Warm-up run
    for _ in range(5):
        optimizer.zero_grad()
        bases = []
        for A in params:
            H = 0.5 * (A + A.mH)
            X = 1j * H
            if use_taylor:
                U = taylor_matrix_exp(X, order=20)
            else:
                U = torch.matrix_exp(X)
            bases.append(U)
        loss = compute_amub_loss(bases, d)
        loss.backward()
        optimizer.step()
    
    if device.type == 'mps':
        torch.mps.synchronize()
        
    start_time = time.perf_counter()
    
    for step in range(steps):
        optimizer.zero_grad()
        bases = []
        for A in params:
            H = 0.5 * (A + A.mH)
            X = 1j * H
            if use_taylor:
                U = taylor_matrix_exp(X, order=20)
            else:
                U = torch.matrix_exp(X)
            bases.append(U)
        loss = compute_amub_loss(bases, d)
        loss.backward()
        optimizer.step()
        
    if device.type == 'mps':
        torch.mps.synchronize()
        
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    # Normalize to 1000 steps
    time_per_1000 = (elapsed / steps) * 1000
    
    return time_per_1000

def main():
    print("Starting Multi-Dimensional CPU and M1 GPU Performance Benchmark...")
    results = {}
    
    # We test multiple dimensions to find the GPU parallelization crossover point
    dimensions = [6, 12, 24, 48, 96]
    
    for d in dimensions:
        print(f"\n--- Benchmarking Dimension d = {d} ---")
        results[d] = {}
        
        # 1. CPU complex128
        print(f"CPU complex128 (d={d})...")
        t128 = run_benchmark_for_config('cpu', torch.complex128, use_taylor=False, d=d)
        print(f"  Time: {t128:.3f}s per 1000 steps")
        results[d]['cpu_complex128'] = t128
        
        # 2. CPU complex64
        print(f"CPU complex64 (d={d})...")
        t64 = run_benchmark_for_config('cpu', torch.complex64, use_taylor=False, d=d)
        print(f"  Time: {t64:.3f}s per 1000 steps")
        results[d]['cpu_complex64'] = t64
        
        # 3. MPS complex64 GPU (Taylor matrix exp)
        if torch.backends.mps.is_available():
            print(f"Apple Silicon M1 GPU MPS complex64 (d={d})...")
            try:
                tmps = run_benchmark_for_config('mps', torch.complex64, use_taylor=True, d=d)
                print(f"  Time: {tmps:.3f}s per 1000 steps")
                results[d]['mps_complex64_taylor'] = tmps
                
                speedup_128 = t128 / tmps
                speedup_64 = t64 / tmps
                print(f"  M1 GPU Speedup vs CPU complex128: {speedup_128:.2f}x")
                print(f"  M1 GPU Speedup vs CPU complex64:  {speedup_64:.2f}x")
                results[d]['speedup_vs_128'] = speedup_128
                results[d]['speedup_vs_64'] = speedup_64
            except Exception as e:
                print(f"  MPS Benchmark failed: {e}")
        else:
            print("  MPS is not available.")
            
    # Save benchmark results to JSON
    with open('marimo/results_d6_amub_precision_campaign/hardware_benchmarks.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("\nMulti-dimensional benchmarks saved to marimo/results_d6_amub_precision_campaign/hardware_benchmarks.json")

if __name__ == "__main__":
    main()
