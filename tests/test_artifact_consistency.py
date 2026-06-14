import pytest
import numpy as np
import torch
import json
import sys
from pathlib import Path

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.loss import total_amub_loss

def test_artifact_consistency():
    run_dir = Path(__file__).parent.parent / "results" / "runs" / "d6_n4_complex128_seed3"
    
    # Assert run folder components exist
    assert run_dir.exists()
    bases_path = run_dir / "best_bases.npy"
    meta_path = run_dir / "run_metadata.json"
    
    assert bases_path.exists()
    assert meta_path.exists()
    
    # Load optimized bases
    bases_np = np.load(bases_path)
    # Convert to torch tensor matching the double precision of the run
    bases_torch = torch.from_numpy(bases_np)
    
    # Load metadata
    with open(meta_path, "r") as f:
        metadata = json.load(f)
        
    recorded_loss = metadata["best_loss"]
    dimension = metadata["dimension"]
    
    # Recompute loss
    recomputed_loss = total_amub_loss(bases_torch, dimension).item()
    
    # Assert recomputed loss matches recorded loss to high numerical precision
    assert np.isclose(recomputed_loss, recorded_loss, atol=1e-12, rtol=1e-12)
