#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.config import load_config
from src.amub.experiment import run_single_experiment
from src.amub.io_utils import make_run_dir, save_run_artifacts, save_csv

def main():
    parser = argparse.ArgumentParser(description="Run both double and single precision AMUB campaigns.")
    parser.add_argument("--config128", type=str, default="configs/multiseed_complex128.yaml", help="Path to complex128 config.")
    parser.add_argument("--config64", type=str, default="configs/multiseed_complex64.yaml", help="Path to complex64 config.")
    parser.add_argument("--quick", action="store_true", help="Run a quick smoke version.")
    args = parser.parse_args()

    configs = {
        "complex128": load_config(args.config128),
        "complex64": load_config(args.config64)
    }
    
    summary_rows = []
    
    for dtype_name, config in configs.items():
        output_root = Path(config.get("output_root", "results/runs"))
        output_root.mkdir(parents=True, exist_ok=True)
        
        n_values = config.get("n_values", [3, 4, 5, 6])
        seeds = config.get("seeds", [0, 1, 2, 3, 4])
        
        if args.quick:
            n_values = [3]
            seeds = [0, 1]
            config.steps = 50
            
        for n in n_values:
            for seed in seeds:
                print(f"\n==========================================")
                # Dynamic device allocation matches the dynamically queries backend
                print(f"Precision Campaign Run: n={n}, seed={seed}, dtype={dtype_name}")
                print(f"==========================================")
                
                config._raw["n_bases"] = n
                config._raw["seed"] = seed
                
                run_result = run_single_experiment(config)
                
                # Make path and write out artifacts
                run_dir = make_run_dir(output_root, config.get("dimension", 6), n, dtype_name, seed)
                save_run_artifacts(run_result, run_dir)
                
                meta = run_result["metadata"]
                summary_rows.append({
                    "dimension": meta["dimension"],
                    "n_bases": meta["n_bases"],
                    "seed": meta["seed"],
                    "dtype": meta["dtype"],
                    "best_loss": meta["best_loss"],
                    "near_exact_pairs_primary": meta["near_exact_pairs_primary"],
                    "unitarity_residual_max": meta["unitarity_residual_max"],
                    "total_elapsed_seconds": meta["total_elapsed_seconds"],
                })
                
    # Save the aggregated precision comparison summary
    summary_dir = Path("results/summaries")
    summary_dir.mkdir(parents=True, exist_ok=True)
    save_csv(summary_rows, summary_dir / "precision_comparison_summary.csv")
    print(f"\nPrecision campaign completed. Summary saved to: {summary_dir / 'precision_comparison_summary.csv'}")

if __name__ == "__main__":
    main()
