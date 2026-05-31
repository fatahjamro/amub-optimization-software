#!/usr/bin/env python3
"""
Utility script to regenerate and export all key figures for the ACM TOMS paper
as high-quality vector PDFs and PNGs.

Run this script from the workspace root or the marimo directory:
    python3 marimo/export_figures.py
"""

import json
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def get_paths():
    # Detect if run from workspace root or marimo subdirectory
    current_dir = Path(__file__).parent.resolve()
    if current_dir.name == "marimo":
        workspace_root = current_dir.parent
    else:
        workspace_root = current_dir
        
    output_root = workspace_root / "marimo" / "results_d6_amub_precision_campaign"
    figure_dir = output_root / "paper_figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    return workspace_root, output_root, figure_dir

def plot_precision_loss_summary(precision_summary_rows, figure_dir):
    print("Generating Loss Summary plot...")
    dtype_order = ["complex128", "complex64"]
    fig, axis_handle = plt.subplots(figsize=(7.0, 4.5))

    for dtype_label in dtype_order:
        dtype_rows = [row for row in precision_summary_rows if row["dtype"] == dtype_label]
        dtype_rows = sorted(dtype_rows, key=lambda row: row["n_bases"])
        if not dtype_rows:
            continue

        n_values_for_plot = np.array([row["n_bases"] for row in dtype_rows], dtype=float)
        median_losses = np.array([row["loss_median"] for row in dtype_rows], dtype=float)
        min_losses = np.array([row["loss_min"] for row in dtype_rows], dtype=float)
        max_losses = np.array([row["loss_max"] for row in dtype_rows], dtype=float)

        lower_errors = median_losses - min_losses
        upper_errors = max_losses - median_losses

        axis_handle.errorbar(
            n_values_for_plot,
            median_losses,
            yerr=[lower_errors, upper_errors],
            marker="o",
            capsize=4,
            label=dtype_label,
        )

    axis_handle.set_xlabel(r"Number of candidate bases $n$")
    axis_handle.set_ylabel(r"Best loss $\mathcal{L}_n$")
    axis_handle.set_title(r"Multi-seed AMUB loss summary in $d=6$")
    axis_handle.set_xticks([3, 4, 5, 6])
    axis_handle.legend()
    axis_handle.grid(True, alpha=0.3)

    png_path = figure_dir / "loss_summary_by_n_precision.png"
    pdf_path = figure_dir / "loss_summary_by_n_precision.pdf"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")

def plot_near_exact_pair_summary(precision_summary_rows, figure_dir):
    print("Generating Near-Exact Pair Summary plot...")
    dtype_order = ["complex128", "complex64"]
    fig, axis_handle = plt.subplots(figsize=(7.0, 4.5))

    for dtype_label in dtype_order:
        dtype_rows = [row for row in precision_summary_rows if row["dtype"] == dtype_label]
        dtype_rows = sorted(dtype_rows, key=lambda row: row["n_bases"])
        if not dtype_rows:
            continue

        n_values_for_plot = np.array([row["n_bases"] for row in dtype_rows], dtype=float)
        median_counts = np.array([row["near_exact_median"] for row in dtype_rows], dtype=float)
        min_counts = np.array([row["near_exact_min"] for row in dtype_rows], dtype=float)
        max_counts = np.array([row["near_exact_max"] for row in dtype_rows], dtype=float)

        lower_errors = median_counts - min_counts
        upper_errors = max_counts - median_counts

        axis_handle.errorbar(
            n_values_for_plot,
            median_counts,
            yerr=[lower_errors, upper_errors],
            marker="o",
            capsize=4,
            label=dtype_label,
        )

    axis_handle.set_xlabel(r"Number of candidate bases $n$")
    axis_handle.set_ylabel("Number of near-exact MUB pairs")
    axis_handle.set_title(r"Near-exact pair counts in $d=6$")
    axis_handle.set_xticks([3, 4, 5, 6])
    axis_handle.set_ylim(bottom=-0.2)
    axis_handle.legend()
    axis_handle.grid(True, alpha=0.3)

    png_path = figure_dir / "near_exact_pair_summary_by_n_precision.png"
    pdf_path = figure_dir / "near_exact_pair_summary_by_n_precision.pdf"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")

def plot_sorted_pairwise_loss_spectra(manifest_path, output_root, figure_dir, figure_name, display_zero_tol):
    print(f"Generating sorted pairwise loss spectra: {figure_name}...")
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}. Skipping.")
        return

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    items = list(manifest.items())
    num_items = len(items)
    if num_items == 0:
        return

    num_cols = 2
    num_rows = int(np.ceil(num_items / num_cols))

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(7.2 * num_cols, 3.8 * num_rows), squeeze=False)
    axes_flat = axes.flatten()
    figure_records = {}

    for idx, (label, entry) in enumerate(items):
        ax = axes_flat[idx]
        # Resolve and validate paths dynamically using abspath to prevent path traversal
        diag_relative = str(entry["pairwise_diagnostics_path"])
        
        # Proactive Input Validation: Instantly block directory traversal patterns and absolute paths in the raw input
        if ".." in diag_relative or diag_relative.startswith("/") or diag_relative.startswith("\\") or ":" in diag_relative:
            raise ValueError(f"Security Violation: Potential path traversal or absolute path detected in raw input: {diag_relative}")
        
        # Primary path construction
        diag_abs = os.path.abspath(os.path.join(str(output_root.parent), "marimo", diag_relative))
        
        # Security Validation: Verify the resolved path resides strictly inside the workspace boundary
        workspace_abs = os.path.abspath(str(output_root.parent.parent))
        if not diag_abs.startswith(workspace_abs):
            raise ValueError(f"Security Violation: Path traversal attempt detected: {diag_abs}")
            
        diag_path = Path(diag_abs)

        if not diag_path.exists():
            # Fallback path construction using string operations to prevent taint flow
            target_marker = "results_d6_amub_precision_campaign"
            if target_marker in diag_relative:
                # Split and extract the relative suffix securely
                relative_suffix = diag_relative.split(target_marker, 1)[1].lstrip("/\\")
                diag_abs_fallback = os.path.abspath(os.path.join(str(output_root), relative_suffix))
                
                # Security Validation: Verify the resolved fallback path resides strictly inside the workspace boundary
                if not diag_abs_fallback.startswith(workspace_abs):
                    raise ValueError(f"Security Violation: Path traversal attempt in fallback detected: {diag_abs_fallback}")
                diag_path = Path(diag_abs_fallback)

        if not diag_path.exists():
            ax.axis("off")
            print(f"Missing diagnostics: {diag_path}")
            continue

        with open(os.path.abspath(diag_path), "r") as f_diag:
            diagnostics = json.load(f_diag)

        diagnostics_sorted = sorted(diagnostics, key=lambda e: float(e["pair_loss"]), reverse=True)
        raw_losses = np.array([float(e["pair_loss"]) for e in diagnostics_sorted], dtype=float)
        display_losses = np.where(raw_losses < display_zero_tol, 0.0, raw_losses)
        pair_labels = [f"({e['pair'][0]},{e['pair'][1]})" for e in diagnostics_sorted]

        x = np.arange(len(display_losses))
        ax.bar(x, display_losses)
        ax.set_xticks(x)
        ax.set_xticklabels(pair_labels, rotation=75, ha="right")

        n_val = int(entry["n_bases"])
        seed_val = int(entry["seed"])
        loss_val = float(entry["best_loss"])
        near_exact_val = int(entry["num_near_exact_pairs"])

        loss_text = f"{loss_val:.3e}" if abs(loss_val) < 1.0e-6 else f"{loss_val:.6f}"
        ax.set_title(f"{label}\nn={n_val}, seed={seed_val}, loss={loss_text}, near-exact={near_exact_val}")
        ax.set_ylabel(r"Pairwise loss $\ell_{ij}$")
        ax.grid(True, axis="y", alpha=0.3)

        if np.max(display_losses) == 0.0:
            ax.set_ylim(0.0, 1.0e-6)

        figure_records[label] = {
            "n_bases": n_val,
            "seed": seed_val,
            "best_loss": loss_val,
            "num_near_exact_pairs": near_exact_val,
            "display_zero_tol": display_zero_tol,
            "pair_losses_raw_sorted": raw_losses.tolist(),
            "pair_labels_sorted": pair_labels,
        }

    for ax in axes_flat[num_items:]:
        ax.axis("off")

    fig.suptitle(r"Sorted pairwise AMUB loss spectra for representative configurations", y=1.02)
    fig.tight_layout()

    png_path = figure_dir / f"{figure_name}.png"
    pdf_path = figure_dir / f"{figure_name}.pdf"
    json_path = figure_dir / f"{figure_name}_data.json"

    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    with open(json_path, "w") as f_out:
        json.dump(figure_records, f_out, indent=2)

    plt.close(fig)
    print(f"Saved: {pdf_path}")

def main():
    workspace_root, output_root, figure_dir = get_paths()
    print(f"Workspace Root: {workspace_root}")
    print(f"Output Root: {output_root}")
    print(f"Figure Directory: {figure_dir}")

    # Load campaign summary rows
    summary_path = output_root / "precision_comparison_d6_n3_to_n6" / "precision_comparison_d6_n3_to_n6.json"
    if not summary_path.exists():
        print(f"Summary JSON not found at {summary_path}. Run the notebook first.")
        return

    with open(summary_path, "r") as f:
        precision_summary_rows = json.load(f)

    # Plot loss summary & near-exact summaries
    plot_precision_loss_summary(precision_summary_rows, figure_dir)
    plot_near_exact_pair_summary(precision_summary_rows, figure_dir)

    # Plot sorted pairwise loss spectra for complex128
    manifest_c128 = output_root / "multiseed_d6_n3_to_n6_complex128" / "representative_runs_for_heatmaps.json"
    plot_sorted_pairwise_loss_spectra(
        manifest_c128, 
        output_root, 
        figure_dir, 
        "sorted_pairwise_loss_spectra_representatives_clean", 
        display_zero_tol=1.0e-20
    )

    # Plot sorted pairwise loss spectra for complex64
    manifest_c64 = output_root / "multiseed_d6_n3_to_n6_complex64" / "representative_runs_for_heatmaps.json"
    plot_sorted_pairwise_loss_spectra(
        manifest_c64, 
        output_root, 
        figure_dir, 
        "sorted_pairwise_loss_spectra_representatives_complex64_clean_tol1e10", 
        display_zero_tol=1.0e-10
    )

    print("\nAll figures exported successfully!")

if __name__ == "__main__":
    main()
