import torch

def entrywise_squared_modulus(X: torch.Tensor) -> torch.Tensor:
    """
    Compute the entrywise squared modulus of a matrix: |X|^2.
    """
    return torch.abs(X) ** 2

def pairwise_overlap(U_i: torch.Tensor, U_j: torch.Tensor) -> torch.Tensor:
    """
    Compute the entrywise squared modulus of transition matrix between U_i and U_j:
    | U_i† U_j |^2.
    """
    return entrywise_squared_modulus(U_i.mH @ U_j)

def pairwise_loss(U_i: torch.Tensor, U_j: torch.Tensor, d: int) -> torch.Tensor:
    """
    Compute the Frobenius norm squared deviation from mutually unbiased condition:
    || |U_i† U_j|^2 - (1/d) * J ||_F^2
    """
    overlaps = pairwise_overlap(U_i, U_j)
    
    # Infer the appropriate real float dtype from the complex matrix U_i
    real_dtype = torch.float64 if U_i.dtype == torch.complex128 else torch.float32
    overlaps = overlaps.to(real_dtype)
    
    target = torch.tensor(1.0 / d, dtype=real_dtype, device=U_i.device)
    loss = torch.sum((overlaps - target) ** 2)
    return loss

def total_amub_loss(bases, d: int) -> torch.Tensor:
    """
    Compute the total approximate MUB loss over all unordered pairs of bases.
    Supports list of bases or a stacked basis tensor.
    """
    n = len(bases)
    real_dtype = torch.float64 if bases[0].dtype == torch.complex128 else torch.float32
    
    total_loss = torch.zeros((), dtype=real_dtype, device=bases[0].device)
    for i in range(n):
        for j in range(i + 1, n):
            total_loss = total_loss + pairwise_loss(bases[i], bases[j], d)
            
    return total_loss

def all_pairwise_losses(bases, d: int):
    """
    Compute individual pairwise AMUB loss contributions for all unordered pairs.
    Returns a list of dictionaries with key 'pair' (i, j) and 'pair_loss' (float).
    """
    n = len(bases)
    contributions = []
    with torch.no_grad():
        for i in range(n):
            for j in range(i + 1, n):
                loss_val = pairwise_loss(bases[i], bases[j], d)
                contributions.append({
                    "pair": (i, j),
                    "pair_loss": float(loss_val.detach().cpu().item())
                })
    return contributions

# Backwards compatibility wrappers matching the Marimo notebook signatures
def pairwise_amub_loss(bases, target_overlap: float) -> torch.Tensor:
    d = int(round(1.0 / target_overlap))
    return total_amub_loss(bases, d)

def pairwise_loss_contributions(bases, target_overlap: float):
    d = int(round(1.0 / target_overlap))
    return all_pairwise_losses(bases, d)
