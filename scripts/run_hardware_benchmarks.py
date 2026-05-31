#!/usr/bin/env python3
import argparse
import time
from pathlib import Path
import sys
import torch

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.config import load_config
from src.amub.model import UnanchoredAMUBModel
from src.amub.loss import total_amub_loss
from src.amub.io_utils import save_csv, save_json

def run_timing_trial(d: int, n: int, dtype_name: str, matrix_exp_backend: str, device_name: str, steps: int) -> float:
    """
    Run a timing trial for the given backend config and return elapsed seconds.
    """
    dtype = torch.complex128 if dtype_name == "complex128" else torch.complex64
    device = torch.device(device_name)
    
    # Initialize the model on the correct device
    model = UnanchoredAMUBModel(
        d=d,
        n_bases=n,
        dtype=dtype,
        init_scale=0.05,
        matrix_exp_backend=matrix_exp_backend,
        device=device
    )
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    
    # Warmup step
    bases = model()
    loss = total_amub_loss(bases, d)
    loss.backward()
    optimizer.step()
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        # Synchronize for MPS timing accuracy
        torch.zeros(1, device=device) + 1
        
    start_time = time.perf_counter()
    
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        bases = model()
        loss = total_amub_loss(bases, d)
        loss.backward()
        optimizer.step()
        
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        torch.zeros(1, device=device) + 1
        
    elapsed = time.perf_counter() - start_time
    return elapsed

def main():
    parser = argparse.ArgumentParser(description="Run CPU/GPU timing benchmarks.")
    parser.add_argument("--config", type=str, default="configs/hardware_benchmarks.yaml", help="Path to config file.")
    parser.add_argument("--quick", action="store_true", help="Run a quick smoke test version.")
    args = parser.parse_args()

    config = load_config(args.config)
    output_root = Path(config.get("output_root", "results/benchmarks"))
    output_root.mkdir(parents=True, exist_ok=True)
    
    dimensions = config.get("dimensions", [6, 12, 24, 48, 96])
    dtypes = config.get("dtypes", ["complex128", "complex64"])
    n_bases = config.get("n_bases", 6)
    steps = config.get("steps", 1000)
    
    if args.quick:
        print("Running in QUICK smoke-test mode...")
        dimensions = [6, 12]
        steps = 50

    gpu_available = torch.cuda.is_available() or torch.backends.mps.is_available()
    gpu_device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    
    summary_rows = []
    raw_timing_records = []

    for d in dimensions:
        print(f"\nBenchmarking dimension d = {d}...")
        row = {"dimension": d}
        
        for dtype_name in dtypes:
            # 1. CPU Reference Timing
            print(f"  CPU {dtype_name}...")
            cpu_time = run_timing_trial(
                d=d,
                n=n_bases,
                dtype_name=dtype_name,
                matrix_exp_backend="torch_native",
                device_name="cpu",
                steps=steps
            )
            row[f"cpu_{dtype_name}_seconds"] = cpu_time
            raw_timing_records.append({
                "dimension": d,
                "dtype": dtype_name,
                "backend": "cpu",
                "elapsed_seconds": cpu_time,
                "steps": steps,
            })
            
            # 2. GPU Taylor Timing
            if gpu_available and gpu_device != "cpu":
                print(f"  GPU ({gpu_device}) {dtype_name} with Taylor series fallback...")
                gpu_time = run_timing_trial(
                    d=d,
                    n=n_bases,
                    dtype_name=dtype_name,
                    matrix_exp_backend="taylor",
                    device_name=gpu_device,
                    steps=steps
                )
                row[f"gpu_{dtype_name}_seconds"] = gpu_time
                raw_timing_records.append({
                    "dimension": d,
                    "dtype": dtype_name,
                    "backend": gpu_device,
                    "elapsed_seconds": gpu_time,
                    "steps": steps,
                })
            else:
                row[f"gpu_{dtype_name}_seconds"] = "N/A"
                
        summary_rows.append(row)
        
    # Save results to output root directory
    save_csv(summary_rows, summary_root := (output_root.parent / "summaries" / "hardware_benchmark_summary.csv"))
    save_json(raw_timing_records, output_root / "raw_benchmarks.json")
    
    print(f"\nBenchmark completed. Summary saved to: {summary_root}")
    print(summary_rows)

if __name__ == "__main__":
    main()
