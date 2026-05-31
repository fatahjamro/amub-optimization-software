import pytest
import torch
import sys
from pathlib import Path

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.model import UnanchoredAMUBModel
from src.amub.loss import total_amub_loss, all_pairwise_losses

def test_loss_properties():
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
        device=device
    )
    
    bases = model.bases()
    total_loss_val = total_amub_loss(bases, d)
    
    # Loss must be strictly non-negative
    assert total_loss_val.item() >= 0.0
    
    # Loss must follow the accumulation dtype matching the complex precision
    assert total_loss_val.dtype == torch.float64
    
    # The sum of pairwise loss contributions must equal total loss
    contributions = all_pairwise_losses(bases, d)
    sum_contributions = sum(c["pair_loss"] for c in contributions)
    
    assert abs(total_loss_val.item() - sum_contributions) < 1.0e-12
