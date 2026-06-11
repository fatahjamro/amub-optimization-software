#!/usr/bin/env parser
import argparse
import json
from pathlib import Path
import numpy as np
import sys

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.io_utils import save_csv, save_json

def main():
    parser = argparse.ArgumentParser(description="Aggregate and summarize AMUB campaign runs.")
    parser.add_argument("--results-root", type=str, default="results/runs", help="Directory containing run directories.")
    args = parser.parse_args()

    results_path = Path(args.results_root)
    if not results_path.exists():
        print(f"Results directory not found: {results_path}")
        return

    # Find all run metadata files
    metadata_files = list(results_path.glob("**/run_metadata.json"))
    if not metadata_files:
        print(f"No run_metadata.json files found under {results_path}")
        return

    # Group runs by (dtype, n_bases)
    groups = {}
    for meta_file in metadata_files:
        with open(meta_file, "r") as f:
            meta = json.load(f)
        
        dtype = meta["dtype"]
        n_bases = meta["n_bases"]
        dimension = meta.get("dimension", 6)
        key = (dimension, dtype, n_bases)
        
        if key not in groups:
            groups[key] = []
        groups[key].append(meta)

    # Compute summaries for each group
    summary_rows_128 = []
    summary_rows_64 = []
    precision_comparison_rows = []

    for (dimension, dtype, n_bases), runs in sorted(groups.items()):
        losses = [run["best_loss"] for run in runs]
        near_exacts = [run["near_exact_pairs_primary"] for run in runs]
        
        loss_min = float(np.min(losses))
        loss_median = float(np.median(losses))
        loss_max = float(np.max(losses))
        
        near_exact_min = float(np.min(near_exacts))
        near_exact_median = float(np.median(near_exacts))
        near_exact_max = float(np.max(near_exacts))
        
        summary_row = {
            "dimension": dimension,
            "n_bases": n_bases,
            "dtype": dtype,
            "loss_min": loss_min,
            "loss_median": loss_median,
            "loss_max": loss_max,
            "near_exact_min": near_exact_min,
            "near_exact_median": near_exact_median,
            "near_exact_max": near_exact_max,
            "num_seeds": len(runs),
        }
        
        precision_comparison_rows.append(summary_row)
        
        if dtype == "complex128":
            summary_rows_128.append(summary_row)
        else:
            summary_rows_64.append(summary_row)

    # Write CSV summaries under results/summaries/
    summaries_dir = results_path.parent / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    
    save_csv(summary_rows_128, summaries_dir / "multiseed_complex128_summary.csv")
    save_csv(summary_rows_64, summaries_dir / "multiseed_complex64_summary.csv")
    save_csv(precision_comparison_rows, summaries_dir / "precision_comparison_summary.csv")
    
    # Save precision_comparison_rows JSON under results/precision_comparison_d6_n3_to_n6/
    legacy_dir = results_path.parent / "precision_comparison_d6_n3_to_n6"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    save_json(precision_comparison_rows, legacy_dir / "precision_comparison_d6_n3_to_n6.json")
    
    # Also save representative heatmap manifests to make plotting.plot_sorted_pairwise_loss_spectra work out-of-the-box
    for dtype in ["complex128", "complex64"]:
        rep_manifest = {}
        for (grp_dim, grp_dtype, n_bases), runs in groups.items():
            if grp_dtype != dtype:
                continue
            
            # Find the representative run (seed with best/median loss)
            best_run = min(runs, key=lambda r: r["best_loss"])
            label = f"d{grp_dim}_n{n_bases}_{dtype}_seed{best_run['seed']}"
            
            # Define relative diagnostics paths for plotting script
            diag_path = f"d{grp_dim}_n{n_bases}_{dtype}_seed{best_run['seed']}/pairwise_diagnostics.json"
            overlaps_path = f"d{grp_dim}_n{n_bases}_{dtype}_seed{best_run['seed']}/pairwise_overlaps.npz"
            
            rep_manifest[label] = {
                "n_bases": n_bases,
                "seed": best_run["seed"],
                "best_loss": best_run["best_loss"],
                "num_near_exact_pairs": best_run["near_exact_pairs_primary"],
                "pairwise_diagnostics_path": diag_path,
                "pairwise_overlaps_path": overlaps_path,
            }
            
        # We save this to a directory based on the dimension found in the group
        # Defaults to d6 if empty
        representative_d = 6
        if runs:
            representative_d = best_run.get("dimension", 6)
            
        legacy_campaign_dir = results_path / f"multiseed_d{representative_d}_n3_to_n6_{dtype}"
        legacy_campaign_dir.mkdir(parents=True, exist_ok=True)
        save_json(rep_manifest, legacy_campaign_dir / "representative_runs_for_heatmaps.json")

    print("\nAggregation completed successfully!")
    print(f"Aggregated {len(metadata_files)} run(s) into summaries:")
    print(f"  - {summaries_dir / 'precision_comparison_summary.csv'}")
    print(f"  - {legacy_dir / 'precision_comparison_d6_n3_to_n6.json'}")

if __name__ == "__main__":
    main()
