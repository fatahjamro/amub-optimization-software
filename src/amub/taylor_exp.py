import torch
import math

def taylor_matrix_exp(X: torch.Tensor, order: int = 20) -> torch.Tensor:
    """
    Compute matrix exponential via Taylor series expansion.
    Preserves device and complex precision.
    """
    eye = torch.eye(X.shape[-1], dtype=X.dtype, device=X.device)
    term = eye
    result = eye
    for i in range(1, order + 1):
        term = term @ X / i
        result = result + term
    return result

def taylor_truncation_bound(norm_x: float, order: int = 20) -> float:
    """
    Calculate the theoretical upper bound on the truncation error:
    E_N <= (||X||^(N+1) / (N+1)!) * e^(||X||).
    """
    if norm_x <= 0:
        return 0.0
    
    n_plus_1 = order + 1
    fact = math.factorial(n_plus_1)
    bound = (norm_x ** n_plus_1) / fact * math.exp(norm_x)
    return bound

def compare_taylor_to_torch(H: torch.Tensor, order: int = 20) -> float:
    """
    Compare Taylor series exponentiation to PyTorch native matrix_exp:
    || Taylor(1j * H) - exp(1j * H) ||_F.
    """
    X = 1j * H
    taylor_val = taylor_matrix_exp(X, order=order)
    torch_val = torch.matrix_exp(X)
    diff = torch.linalg.matrix_norm(taylor_val - torch_val, ord="fro")
    return float(diff.detach().cpu().item())
