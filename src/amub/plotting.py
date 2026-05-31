import json
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def plot_precision_loss_summary(precision_summary_rows, figure_dir: Path):
    """
    Plot best AMUB loss summary with error bars across n and floating-point precisions.
    """
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

    figure_dir.mkdir(parents=True, exist_ok=True)
    png_path = figure_dir / "loss_summary_by_n_precision.png"
    pdf_path = figure_dir / "loss_summary_by_n_precision.pdf"
    
    # Save both figure-data JSON and actual figures
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")

def plot_near_exact_pair_summary(precision_summary_rows, figure_dir: Path):
    """
    Plot near-exact MUB pair counts across n and floating-point precisions.
    """
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

    figure_dir.mkdir(parents=True, exist_ok=True)
    png_path = figure_dir / "near_exact_pair_summary_by_n_precision.png"
    pdf_path = figure_dir / "near_exact_pair_summary_by_n_precision.pdf"
    
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")

def plot_sorted_pairwise_loss_spectra(manifest_path: Path, output_root: Path, figure_dir: Path, figure_name: str, display_zero_tol: float):
    """
    Generate sorted pairwise loss spectra subplots for representative configurations.
    """
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
        diag_relative = str(entry["pairwise_diagnostics_path"])
        
        # Security validation against directory traversal
        if ".." in diag_relative or diag_relative.startswith("/") or diag_relative.startswith("\\") or ":" in diag_relative:
            raise ValueError(f"Security Violation: Path traversal or absolute path detected in input: {diag_relative}")
            
        diag_path = output_root / diag_relative
        if not diag_path.exists():
            # Fallback path construct
            diag_path = Path(os.path.abspath(os.path.join(str(output_root), diag_relative)))

        if not diag_path.exists():
            ax.axis("off")
            print(f"Missing diagnostics: {diag_path}")
            continue

        with open(diag_path, "r") as f_diag:
            diagnostics = json.load(f_diag)

        # Support both old ('pair_loss') and new ('loss') keys
        diagnostics_sorted = sorted(diagnostics, key=lambda e: float(e.get("pair_loss", e.get("loss", 0.0))), reverse=True)
        raw_losses = np.array([float(e.get("pair_loss", e.get("loss", 0.0))) for e in diagnostics_sorted], dtype=float)
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

    figure_dir.mkdir(parents=True, exist_ok=True)
    png_path = figure_dir / f"{figure_name}.png"
    pdf_path = figure_dir / f"{figure_name}.pdf"
    
    # Save figures
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    
    # Save figure data
    json_path = figure_dir.parent / "figure_data" / f"{figure_name}_data.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f_out:
        json.dump(figure_records, f_out, indent=2)

    plt.close(fig)
    print(f"Saved: {pdf_path}")

def plot_pairwise_overlap_heatmaps_from_npz(*, overlaps_npz_path: Path, title: str, output_path_base: Path, target_overlap: float, fixed_vmax: float = None):
    """
    Plot all pairwise overlap matrices stored in a .npz file.
    """
    overlap_archive = np.load(overlaps_npz_path)

    pair_keys = sorted(
        overlap_archive.files,
        key=lambda key_name: tuple(
            int(part) for part in key_name.replace("pair_", "").split("_")
        ),
    )

    num_pairs = len(pair_keys)
    if num_pairs == 0:
        print(f"No pairwise overlaps found in {overlaps_npz_path}")
        return None

    # Choose grid automatically
    num_cols = min(4, num_pairs)
    num_rows = int(np.ceil(num_pairs / num_cols))

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(3.2 * num_cols, 3.0 * num_rows), squeeze=False)
    axes_flat = axes.flatten()

    vmax_value = fixed_vmax if fixed_vmax is not None else 2.0 * target_overlap
    image_handle = None

    for axis_index, pair_key in enumerate(pair_keys):
        axis_handle = axes_flat[axis_index]
        overlap_matrix = overlap_archive[pair_key]

        pair_label = pair_key.replace("pair_", "(").replace("_", ",") + ")"

        image_handle = axis_handle.imshow(
            overlap_matrix,
            vmin=0.0,
            vmax=vmax_value,
        )

        axis_handle.set_title(f"Pair {pair_label}")
        axis_handle.set_xticks([])
        axis_handle.set_yticks([])

    for unused_axis in axes_flat[num_pairs:]:
        unused_axis.axis("off")

    fig.suptitle(title)
    fig.colorbar(
        image_handle,
        ax=axes_flat.tolist(),
        shrink=0.75,
        label=r"$|U_i^\dagger U_j|^2$",
    )

    output_path_base.parent.mkdir(parents=True, exist_ok=True)
    png_path = output_path_base.with_suffix(".png")
    pdf_path = output_path_base.with_suffix(".pdf")

    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    return {
        "png": str(png_path),
        "pdf": str(pdf_path),
        "num_pairs": num_pairs,
    }

def plot_all_representative_heatmaps(*, representative_manifest_path: Path, output_root: Path, d: int):
    """
    Load representative run manifest and generate heatmaps.
    """
    with open(representative_manifest_path, "r") as f:
        representative_manifest = json.load(f)

    heatmap_output_dir = output_root / "heatmap_figures_representative_runs"
    heatmap_output_dir.mkdir(parents=True, exist_ok=True)

    figure_records = {}
    target = 1.0 / d

    print("\nGenerating representative heatmap figures...")
    for label, entry in representative_manifest.items():
        overlaps_path = Path(entry["pairwise_overlaps_path"])
        if not overlaps_path.is_absolute():
            overlaps_path = output_root / overlaps_path

        if not overlaps_path.exists():
            print(f"  overlaps path not found: {overlaps_path}. Skipping.")
            continue

        n_val = int(entry["n_bases"])
        seed_val = int(entry["seed"])
        loss_val = float(entry["best_loss"])
        near_exact_val = int(entry["num_near_exact_pairs"])

        title = f"{label}: d={d}, n={n_val}, seed={seed_val}, loss={loss_val:.6f}, near-exact={near_exact_val}"
        output_path_base = heatmap_output_dir / f"{label}_d{d}_n{n_val}_seed{seed_val}"

        figure_record = plot_pairwise_overlap_heatmaps_from_npz(
            overlaps_npz_path=overlaps_path,
            title=title,
            output_path_base=output_path_base,
            target_overlap=target,
            fixed_vmax=2.0 * target,
        )

        figure_records[label] = {
            "representative": entry,
            "figure": figure_record,
        }

    figure_manifest_path = heatmap_output_dir / "heatmap_figure_manifest.json"
    with open(figure_manifest_path, "w") as f_manifest:
        json.dump(figure_records, f_manifest, indent=2)

    print(f"Heatmap generation complete. Manifest saved to: {figure_manifest_path}")
    return figure_records
