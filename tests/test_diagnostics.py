import pytest
import torch
from math import comb
import sys
from pathlib import Path

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.model import UnanchoredAMUBModel
from src.amub.diagnostics import compute_pairwise_diagnostics, summarize_near_exact_pairs

def test_diagnostics_structure():
    d = 6
    n_bases = 5
    init_scale = 0.05
    dtype = torch.complex128
    device = torch.device("cpu")
    
    model = UnanchoredAMUBModel(
        d=d,
        n_bases=n_bases,
        dtype=dtype,
        init_scale=init_scale,
        device=device
    )
    
    bases = model.bases()
    tolerances = [1e-6, 1e-5, 1e-4]
    
    diagnostics = compute_pairwise_diagnostics(bases, d, tolerances)
    
    # Assert number of diagnostic pairs matches combinatorial unordered pairs: n choose 2
    expected_pairs = comb(n_bases, 2)
    assert len(diagnostics) == expected_pairs
    
    for row in diagnostics:
        assert "pair" in row
        assert len(row["pair"]) == 2
        assert "loss" in row
        assert "delta_max" in row
        assert "near_exact" in row
        
        # Verify all requested tolerances are classified
        for tol in tolerances:
            assert str(tol) in row["near_exact"]
            
    summary = summarize_near_exact_pairs(diagnostics, 1e-6)
    assert "num_near_exact_pairs" in summary
    assert "num_defective_pairs" in summary
    assert summary["num_near_exact_pairs"] + summary["num_defective_pairs"] == expected_pairs
