import torch
import torch.nn as nn
from .taylor_exp import taylor_matrix_exp

class UnanchoredAMUBModel(nn.Module):
    """
    Unanchored AMUB model representing n orthonormal bases in C^d.
    Each basis is parameterized via Lie-algebra exponentiation:
        U_k = exp(i H_k),
    where H_k is Hermitian symmetrized from a trainable complex matrix A_k:
        H_k = (A_k + A_k†)/2.
    """
    def __init__(self, d: int, n_bases: int, dtype: torch.dtype, init_scale: float, matrix_exp_backend: str = "torch", device: torch.device = None):
        super().__init__()
        self.d = d
        self.n_bases = n_bases
        self.dtype = dtype
        self.matrix_exp_backend = matrix_exp_backend
        
        # Determine device dynamically if not provided (Enhancement 1: Device Agnosticism)
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = device

        # Trainable complex parameters A_k initialized as unconstrained random complex matrices
        self.params = nn.ParameterList([
            nn.Parameter(
                init_scale * torch.randn(d, d, dtype=dtype, device=self.device)
            )
            for _ in range(n_bases)
        ])

    def hermitian_generators(self):
        """
        Return the list of Hermitian generators: H_k = (A_k + A_k†)/2.
        """
        return [0.5 * (A + A.mH) for A in self.params]

    def unitary_from_param(self, A: torch.Tensor) -> torch.Tensor:
        """
        Calculate U_k = exp(i H_k). Auto-routes between native torch and Taylor backend.
        """
        H = 0.5 * (A + A.mH)
        X = 1j * H
        
        # Auto-route to Taylor series on GPU/MPS if taylor is requested or if native torch.matrix_exp is unavailable/slow
        if self.matrix_exp_backend == "taylor" or (X.device.type in ("mps", "cuda") and self.matrix_exp_backend != "torch_native"):
            return taylor_matrix_exp(X, order=20)
        
        return torch.matrix_exp(X)

    def bases(self):
        """
        Return the list of current unitary bases U_1, ..., U_n.
        """
        return [self.unitary_from_param(A) for A in self.params]

    def forward(self) -> torch.Tensor:
        """
        Forward pass: returns all n bases stacked as a single tensor of shape (n, d, d).
        """
        return torch.stack(self.bases())
