import torch
import numpy as np
from .loss import pairwise_overlap, pairwise_loss

def classify_near_exact(delta_ij: float, tau: float) -> bool:
    """
    Returns True if maximum overlap deviation delta_ij is below tolerance tau.
    """
    return bool(delta_ij < tau)

def compute_pairwise_diagnostics(bases, d: int, tolerances):
    """
    Compute comprehensive diagnostics for all unordered pairs (i, j).
    """
    diagnostics = []
    n = len(bases)
    target_val = 1.0 / d
    
    with torch.no_grad():
        for i in range(n):
            for j in range(i + 1, n):
                overlaps = pairwise_overlap(bases[i], bases[j])
                real_dtype = torch.float64 if bases[i].dtype == torch.complex128 else torch.float32
                overlaps = overlaps.to(real_dtype)
                
                deviations = overlaps - target_val
                abs_deviations = torch.abs(deviations)
                
                ell_ij = float(pairwise_loss(bases[i], bases[j], d).detach().cpu().item())
                delta_ij = float(torch.max(abs_deviations).detach().cpu().item())
                
                tol_classification = {}
                for tol in tolerances:
                    tol_str = str(tol)
                    tol_classification[tol_str] = classify_near_exact(delta_ij, tol)
                    
                diagnostics.append({
                    "pair": (i, j),
                    "loss": ell_ij,
                    "delta_max": delta_ij,
                    "near_exact": tol_classification,
                    "min_overlap": float(torch.min(overlaps).detach().cpu().item()),
                    "max_overlap": float(torch.max(overlaps).detach().cpu().item()),
                    "mean_overlap": float(torch.mean(overlaps).detach().cpu().item()),
                    "std_overlap": float(torch.std(overlaps, unbiased=False).detach().cpu().item()),
                })
                
    return diagnostics

# Backwards compatible alias for old codebase
def pairwise_overlap_diagnostics(bases, target_overlap: float):
    d = int(round(1.0 / target_overlap))
    return compute_pairwise_diagnostics(bases, d, [1e-6])

def unitarity_residual(U: torch.Tensor) -> float:
    """
    Compute the Frobenius norm unitarity residual: || U† U - I ||_F.
    """
    d_local = U.shape[-1]
    identity = torch.eye(d_local, dtype=U.dtype, device=U.device)
    residual = torch.linalg.norm(U.mH @ U - identity, ord="fro")
    return float(residual.detach().cpu().item())

def unitarity_diagnostics(bases):
    """
    Compute unitarity residuals for a list of bases.
    """
    residuals = [unitarity_residual(U) for U in bases]
    return {
        "per_basis_unitarity_residuals": residuals,
        "max_unitarity_residual": float(np.max(residuals)),
        "mean_unitarity_residual": float(np.mean(residuals)),
    }

def generator_spectral_norms(H_list):
    """
    Compute spectral norm (ord=2) for each Hermitian matrix in H_list.
    """
    norms = []
    for H in H_list:
        norm = torch.linalg.matrix_norm(H, ord=2)
        norms.append(float(norm.detach().cpu().item()))
    return norms

def generator_norm_diagnostics(model):
    """
    Compute generator norms for the model.
    """
    H_list = model.hermitian_generators()
    norms = generator_spectral_norms(H_list)
    return {
        "per_basis_generator_norms": norms,
        "max_generator_norm": float(np.max(norms)),
        "mean_generator_norm": float(np.mean(norms)),
    }

def summarize_near_exact_pairs(pairwise_diagnostics, near_exact_tol: float):
    """
    Count and list pairs whose maximum absolute deviation is below near_exact_tol.
    """
    near_exact_pairs = []
    defective_pairs = []
    
    for row in pairwise_diagnostics:
        # Support both 'delta_max' (compute_pairwise_diagnostics) and 'max_abs_dev' (old codebase)
        val = row.get("delta_max", row.get("max_abs_dev"))
        if val < near_exact_tol:
            near_exact_pairs.append(row["pair"])
        else:
            defective_pairs.append(row["pair"])
            
    return {
        "near_exact_tol": near_exact_tol,
        "num_near_exact_pairs": len(near_exact_pairs),
        "num_defective_pairs": len(defective_pairs),
        "near_exact_pairs": near_exact_pairs,
        "defective_pairs": defective_pairs,
    }
