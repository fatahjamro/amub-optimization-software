import pytest
import torch
import math
import sys
from pathlib import Path

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.taylor_exp import taylor_matrix_exp, compare_taylor_to_torch, taylor_truncation_bound

def test_taylor_exponential():
    d = 6
    # Construct a small Hermitian matrix
    torch.manual_seed(42)
    A = torch.randn(d, d, dtype=torch.complex128)
    H = 0.5 * (A + A.mH)
    
    # Verify Taylor matrix exponentiation vs native torch.matrix_exp
    diff_frob = compare_taylor_to_torch(H, order=20)
    print(f"Taylor order 20 vs Native torch.matrix_exp difference: {diff_frob:.3e}")
    
    # Order 20 Taylor should match native exponentiation within extremely tight tolerance
    assert diff_frob < 1.0e-9
    
    # Test theoretical truncation bound
    norm_x = float(torch.linalg.matrix_norm(1j * H, ord=2).item())
    bound = taylor_truncation_bound(norm_x, order=20)
    assert bound >= 0.0
    print(f"Theoretical truncation bound: {bound:.3e}")
