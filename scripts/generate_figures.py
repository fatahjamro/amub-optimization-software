#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.plotting import (
    plot_precision_loss_summary,
    plot_near_exact_pair_summary,
    plot_sorted_pairwise_loss_spectra,
    plot_all_representative_heatmaps,
)

def main():
    parser = argparse.ArgumentParser(description="Generate all vector PDF and PNG paper figures from summaries.")
    parser.add_argument("--summary-root", type=str, default="results/summaries", help="Directory containing summary CSV files.")
    parser.add_argument("--output-root", type=str, default="results", help="Parent directory under which figures and runs sit.")
    parser.add_argument("--quick", action="store_true", help="Run in quick smoke test mode.")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    figure_dir = output_root / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load campaign summary JSON
    summary_json_path = output_root / "precision_comparison_d6_n3_to_n6" / "precision_comparison_d6_n3_to_n6.json"
    if not summary_json_path.exists():
        print(f"Summary JSON not found: {summary_json_path}. Skipping campaign plot summaries.")
    else:
        with open(summary_json_path, "r") as f:
            precision_summary_rows = json.load(f)
            
        plot_precision_loss_summary(precision_summary_rows, figure_dir)
        plot_near_exact_pair_summary(precision_summary_rows, figure_dir)

    # 2. Plot sorted pairwise loss spectra for complex128
    manifest_c128 = output_root / "runs" / "multiseed_d6_n3_to_n6_complex128" / "representative_runs_for_heatmaps.json"
    plot_sorted_pairwise_loss_spectra(
        manifest_path=manifest_c128,
        output_root=output_root / "runs",
        figure_dir=figure_dir,
        figure_name="sorted_pairwise_loss_spectra_representatives_clean",
        display_zero_tol=1.0e-20
    )

    # 3. Plot sorted pairwise loss spectra for complex64
    manifest_c64 = output_root / "runs" / "multiseed_d6_n3_to_n6_complex64" / "representative_runs_for_heatmaps.json"
    plot_sorted_pairwise_loss_spectra(
        manifest_path=manifest_c64,
        output_root=output_root / "runs",
        figure_dir=figure_dir,
        figure_name="sorted_pairwise_loss_spectra_representatives_complex64_clean_tol1e10",
        display_zero_tol=1.0e-10
    )

    # 4. Generate all representative heatmaps
    if manifest_c128.exists():
        plot_all_representative_heatmaps(
            representative_manifest_path=manifest_c128,
            output_root=output_root / "runs",
            d=6
        )

    print("\nAll figures generated and saved successfully!")

if __name__ == "__main__":
    main()
