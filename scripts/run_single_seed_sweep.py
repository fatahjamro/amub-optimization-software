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
    parser = argparse.ArgumentParser(description="Run single-seed unanchored AMUB optimization sweeps.")
    parser.add_argument("--config", type=str, default="configs/single_seed_sweep.yaml", help="Path to config file.")
    parser.add_argument("--quick", action="store_true", help="Run a quick smoke test version.")
    args = parser.parse_args()

    config = load_config(args.config)
    output_root = Path(config.get("output_root", "results/runs"))
    output_root.mkdir(parents=True, exist_ok=True)
    
    n_values = config.get("n_values", [2, 3, 4, 5, 6, 7])
    seed = config.get("seeds", [1234])[0]
    
    if args.quick:
        # Override values for a lightning-fast smoke test
        print("Running in QUICK smoke-test mode...")
        n_values = [3, 4]
        config.steps = 50
        
    summary_rows = []
    
    for n in n_values:
        print(f"\n==========================================")
        print(f"Running sweep for n_bases = {n}, seed = {seed}")
        print(f"==========================================")
        
        # Override n_bases and seed dynamically in the config dict
        config._raw["n_bases"] = n
        config._raw["seed"] = seed
        
        run_result = run_single_experiment(config)
        
        # Make path and write out artifacts
        run_dir = make_run_dir(output_root, config.get("dimension", 6), n, config.get("dtype", "complex128"), seed)
        save_run_artifacts(run_result, run_dir)
        
        # Accumulate summary row
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
        
    # Save the aggregated CSV summary
    summary_dir = output_root.parent / "summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    save_csv(summary_rows, summary_dir / "single_seed_sweep.csv")
    print(f"\nSingle-seed sweep completed. Summary saved to: {summary_dir / 'single_seed_sweep.csv'}")

if __name__ == "__main__":
    main()
