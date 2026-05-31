import torch
import sys
from pathlib import Path

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.model import UnanchoredAMUBModel
from src.amub.diagnostics import unitarity_diagnostics

def test_model_unitarity():
    d = 6
    n_bases = 4
    init_scale = 0.05
    dtype = torch.complex128
    device = torch.device("cpu")
    
    model = UnanchoredAMUBModel(
        d=d,
        n_bases=n_bases,
        dtype=dtype,
        init_scale=init_scale,
        matrix_exp_backend="torch_native",
        device=device
    )
    
    bases = model.bases()
    assert len(bases) == n_bases
    
    # Evaluate unitarity residuals
    diag = unitarity_diagnostics(bases)
    print(f"Max unitarity residual: {diag['max_unitarity_residual']}")
    
    # Assert double-precision native exponentiation holds to machine precision
    assert diag["max_unitarity_residual"] < 1.0e-12
    
    # Test complex64 single precision
    model_64 = UnanchoredAMUBModel(
        d=d,
        n_bases=n_bases,
        dtype=torch.complex64,
        init_scale=init_scale,
        device=device
    )
    diag_64 = unitarity_diagnostics(model_64.bases())
    assert diag_64["max_unitarity_residual"] < 1.0e-5
