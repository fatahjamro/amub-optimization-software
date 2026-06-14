import pytest
import numpy as np
import sys
from pathlib import Path

# Add scripts/qpu to the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve() / "scripts" / "qpu"))

from run_quantum_verification import post_process_counts

def test_post_process_counts():
    # 1. Standard counts within valid subspace (0-5)
    counts_valid = {
        "000": 100,  # 0
        "001": 200,  # 1
        "010": 150,  # 2
        "011": 50,   # 3
        "100": 300,  # 4
        "101": 200,  # 5
    }
    # Total valid = 1000
    probs_valid = post_process_counts(counts_valid)
    assert len(probs_valid) == 6
    assert np.isclose(probs_valid[0], 0.1)
    assert np.isclose(probs_valid[1], 0.2)
    assert np.isclose(probs_valid[2], 0.15)
    assert np.isclose(probs_valid[3], 0.05)
    assert np.isclose(probs_valid[4], 0.3)
    assert np.isclose(probs_valid[5], 0.2)
    assert np.isclose(np.sum(probs_valid), 1.0)
    
    # 2. Counts including invalid states (6 = '110', 7 = '111')
    counts_mixed = {
        "000": 100,  # 0
        "001": 200,  # 1
        "010": 150,  # 2
        "011": 50,   # 3
        "100": 300,  # 4
        "101": 200,  # 5
        "110": 500,  # 6 (should be discarded)
        "111": 400,  # 7 (should be discarded)
    }
    # Total valid should still be 1000, and probabilities should be identical
    probs_mixed = post_process_counts(counts_mixed)
    assert len(probs_mixed) == 6
    assert np.isclose(probs_mixed[0], 0.1)
    assert np.isclose(probs_mixed[5], 0.2)
    assert np.isclose(np.sum(probs_mixed), 1.0)
    
    # 3. Fallback case: all counts fall outside valid subspace
    counts_invalid_only = {
        "110": 500,
        "111": 400,
    }
    probs_fallback = post_process_counts(counts_invalid_only)
    assert len(probs_fallback) == 6
    # Should fall back to uniform distribution: 1/6 each
    assert np.allclose(probs_fallback, 1.0 / 6.0)
