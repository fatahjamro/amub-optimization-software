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
    parser = argparse.ArgumentParser(description="Run multi-seed AMUB optimization campaign.")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file.")
    parser.add_argument("--dimension", "-d", type=int, help="Override dimension parameter.")
    parser.add_argument("--n-values", "-n", type=int, nargs="+", help="Override list of candidate bases counts.")
    parser.add_argument("--seeds", type=int, nargs="+", help="Override list of random seeds.")
    parser.add_argument("--quick", action="store_true", help="Run a quick smoke version.")
    args = parser.parse_args()

    config = load_config(args.config)
    
    if args.dimension is not None:
        config._raw["dimension"] = args.dimension
        setattr(config, "dimension", args.dimension)
    if args.n_values is not None:
        config._raw["n_values"] = args.n_values
        setattr(config, "n_values", args.n_values)
    if args.seeds is not None:
        config._raw["seeds"] = args.seeds
        setattr(config, "seeds", args.seeds)

    output_root = Path(config.get("output_root", "results/runs"))
    output_root.mkdir(parents=True, exist_ok=True)
    
    n_values = config.get("n_values", [3, 4, 5, 6])
    seeds = config.get("seeds", [0, 1, 2, 3, 4])
    dtype_name = config.get("dtype", "complex128")
    
    if args.quick:
        print("Running in QUICK smoke-test mode...")
        n_values = [3]
        seeds = [0, 1]
        config.steps = 50
        
    summary_rows = []
    
    for n in n_values:
        for seed in seeds:
            print(f"\n==========================================")
            print(f"Campaign Run: n={n}, seed={seed}, dtype={dtype_name}")
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
            
    # Save the aggregated campaign CSV summary
    summary_dir = output_root.parent / "summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    save_csv(summary_rows, summary_dir / f"multiseed_{dtype_name}_summary.csv")
    print(f"\nCampaign completed. Summary saved to: {summary_dir / f'multiseed_{dtype_name}_summary.csv'}")

if __name__ == "__main__":
    main()
