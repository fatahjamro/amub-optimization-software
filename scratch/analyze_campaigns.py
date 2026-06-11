import json
from pathlib import Path
import numpy as np

results_path = Path("results/runs")
metadata_files = list(results_path.glob("**/run_metadata.json"))

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

for (dimension, dtype, n_bases), runs in sorted(groups.items()):
    losses = [run["best_loss"] for run in runs]
    rounded_losses = [round(l, 6) for l in losses]
    unique_basins = len(set(rounded_losses))
    
    near_exacts = [run["near_exact_pairs_primary"] for run in runs]
    
    print(f"Key: {dtype}, n={n_bases}")
    print(f"  Num seeds: {len(runs)}")
    print(f"  Loss min/med/max: {min(losses):.6f}/{np.median(losses):.6f}/{max(losses):.6f}")
    print(f"  Near-exact min/med/max: {min(near_exacts)}/{np.median(near_exacts)}/{max(near_exacts)}")
    print(f"  Unique basins (rounded 6 decimal places): {unique_basins}")
