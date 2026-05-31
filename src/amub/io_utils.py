import json
import csv
import numpy as np
import torch
from pathlib import Path

def make_run_dir(output_root: str, d: int, n: int, dtype: str, seed: int) -> Path:
    """
    Construct run directory path and create it if it doesn't exist:
        d{d}_n{n}_{dtype}_seed{seed}
    """
    dir_name = f"d{d}_n{n}_{dtype}_seed{seed}"
    run_dir = Path(output_root) / dir_name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def save_json(obj, path):
    """
    Save dictionary/list to a JSON file.
    """
    with open(Path(path), "w") as f:
        json.dump(obj, f, indent=2)

def save_csv(rows, path):
    """
    Save a list of dictionaries to a CSV file.
    """
    if not rows:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def save_run_artifacts(run_result, run_dir: Path):
    """
    Save all artifacts of a single AMUB run.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save best_bases.npy
    bases = run_result["best_bases"]
    if isinstance(bases, torch.Tensor):
        bases_np = bases.detach().cpu().numpy()
    elif isinstance(bases, list):
        bases_np = np.stack([b.detach().cpu().numpy() if isinstance(b, torch.Tensor) else b for b in bases])
    else:
        bases_np = np.array(bases)
        
    np.save(run_dir / "best_bases.npy", bases_np)
    
    # 2. Save pairwise_overlaps.npz
    overlaps_dict = {}
    overlaps = run_result["pairwise_overlaps"]  # List of (pair, matrix) or dict
    if isinstance(overlaps, dict):
        for k, v in overlaps.items():
            overlaps_dict[k] = v.detach().cpu().numpy() if isinstance(v, torch.Tensor) else v
    elif isinstance(overlaps, list):
        for pair, mat in overlaps:
            key = f"pair_{pair[0]}_{pair[1]}"
            overlaps_dict[key] = mat.detach().cpu().numpy() if isinstance(mat, torch.Tensor) else mat
            
    np.savez(run_dir / "pairwise_overlaps.npz", **overlaps_dict)
    
    # 3. Save diagnostics and metadata
    save_json(run_result["pairwise_diagnostics"], run_dir / "pairwise_diagnostics.json")
    save_json(run_result["unitarity_residuals"], run_dir / "unitarity_residuals.json")
    save_json(run_result["generator_norms"], run_dir / "generator_norms.json")
    save_json(run_result["metadata"], run_dir / "run_metadata.json")
    
    # 4. Save optimization history
    save_csv(run_result["optimization_history"], run_dir / "optimization_history.csv")

def load_run_artifacts(run_dir: Path):
    """
    Load saved artifacts from a run directory.
    """
    run_dir = Path(run_dir)
    
    best_bases = np.load(run_dir / "best_bases.npy")
    
    npz_data = np.load(run_dir / "pairwise_overlaps.npz")
    pairwise_overlaps = {k: npz_data[k] for k in npz_data.files}
    
    with open(run_dir / "pairwise_diagnostics.json", "r") as f:
        pairwise_diagnostics = json.load(f)
        
    with open(run_dir / "unitarity_residuals.json", "r") as f:
        unitarity_residuals = json.load(f)
        
    with open(run_dir / "generator_norms.json", "r") as f:
        generator_norms = json.load(f)
        
    with open(run_dir / "run_metadata.json", "r") as f:
        metadata = json.load(f)
        
    optimization_history = []
    with open(run_dir / "optimization_history.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            optimization_history.append({k: float(v) for k, v in row.items()})
            
    return {
        "best_bases": best_bases,
        "pairwise_overlaps": pairwise_overlaps,
        "pairwise_diagnostics": pairwise_diagnostics,
        "unitarity_residuals": unitarity_residuals,
        "generator_norms": generator_norms,
        "metadata": metadata,
        "optimization_history": optimization_history
    }
