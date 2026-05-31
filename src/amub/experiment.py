import time
import random
import platform
from datetime import datetime
from math import comb
import numpy as np
import torch

from .model import UnanchoredAMUBModel
from .loss import total_amub_loss, pairwise_loss_contributions
from .diagnostics import (
    compute_pairwise_diagnostics,
    unitarity_diagnostics,
    generator_norm_diagnostics,
    summarize_near_exact_pairs,
)

def set_random_seed(seed: int):
    """
    Freeze all randomness for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def optimize_model(model: UnanchoredAMUBModel, lr: float, steps: int, log_interval: int, d: int):
    """
    Run unanchored AMUB optimization using the Adam optimizer.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    history = []
    best_loss = float("inf")
    best_bases = None
    max_norm_during_run = 0.0
    
    start_time = time.perf_counter()
    
    for step in range(steps):
        optimizer.zero_grad(set_to_none=True)
        
        # Forward pass
        bases = model()
        loss = total_amub_loss(bases, d)
        loss_val = float(loss.item())
        
        # Backward + Update
        loss.backward()
        optimizer.step()
        
        # Track best solution graph-free
        with torch.no_grad():
            current_norms = generator_norm_diagnostics(model)
            max_norm_during_run = max(max_norm_during_run, current_norms["max_generator_norm"])
            
            if loss_val < best_loss:
                best_loss = loss_val
                best_bases = [U.detach().clone() for U in model.bases()]
                
        # Logging and history
        if step % log_interval == 0 or step == steps - 1:
            elapsed = time.perf_counter() - start_time
            history.append({
                "step": step,
                "current_loss": loss_val,
                "best_loss": best_loss,
                "elapsed_seconds": elapsed,
            })
            
    return best_loss, best_bases, max_norm_during_run, history

def run_single_experiment(config):
    """
    Run a single optimization campaign based on a config dictionary or AMUBConfig object.
    Returns a unified result dictionary.
    """
    # 1. Parse configuration parameters
    d = config.get("dimension", 6)
    n_bases = config.get("n_bases", 4)
    dtype_name = config.get("dtype", "complex128")
    seed = config.get("seed", 1234)
    init_scale = config.get("initialization_scale", 0.05)
    lr = config.get("learning_rate", 0.02)
    log_interval = config.get("log_interval", 100)
    matrix_exp_backend = config.get("matrix_exp_backend", "torch_native")
    
    # Extract steps configuration (can be a dictionary depending on N value or a flat int)
    steps_config = config.get("steps", 1500)
    if isinstance(steps_config, dict):
        steps = steps_config.get("n_lt_5", 1500) if n_bases < 5 else steps_config.get("n_ge_5", 2000)
    else:
        steps = steps_config
        
    near_exact_tolerances = config.get("near_exact_tolerances", [1.0e-6, 1.0e-5, 1.0e-4])
    primary_tolerance = config.get("primary_tolerance", 1.0e-6)
    
    # 2. Setup Device & Seed
    backend_type = config.get("backend", "cpu")
    if backend_type == "cpu":
        device = torch.device("cpu")
    else:
        # Enhancement 1: Dynamic Device allocation with fallback
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
            
    set_random_seed(seed)
    
    # 3. Determine DataType
    dtype = torch.complex128 if dtype_name == "complex128" else torch.complex64
    
    # 4. Instantiate Model
    model = UnanchoredAMUBModel(
        d=d,
        n_bases=n_bases,
        dtype=dtype,
        init_scale=init_scale,
        matrix_exp_backend=matrix_exp_backend,
        device=device,
    )
    
    # 5. Execute Optimization Sweep
    start_wall_time = time.time()
    best_loss, best_bases, max_norm_during_run, history = optimize_model(
        model=model,
        lr=lr,
        steps=steps,
        log_interval=log_interval,
        d=d,
    )
    elapsed_total = time.time() - start_wall_time
    
    # 6. Gather Post-Run Diagnostics
    pairwise_diagnostics = compute_pairwise_diagnostics(best_bases, d, near_exact_tolerances)
    unitarity_residuals = unitarity_diagnostics(best_bases)
    generator_norms = generator_norm_diagnostics(model)
    near_exact_summary = summarize_near_exact_pairs(pairwise_diagnostics, primary_tolerance)
    
    # Stack best bases for npz overlap construction
    pairwise_overlaps = []
    with torch.no_grad():
        for i in range(len(best_bases)):
            for j in range(i + 1, len(best_bases)):
                overlap = torch.abs(best_bases[i].mH @ best_bases[j]) ** 2
                pairwise_overlaps.append(((i, j), overlap))
                
    # 7. Package ACM TOMS submission metadata
    metadata = {
        "artifact_schema_version": "1.0",
        "dimension": d,
        "n_bases": n_bases,
        "seed": seed,
        "dtype": dtype_name,
        "backend": backend_type,
        "device_used": str(device),
        "matrix_exp_backend": matrix_exp_backend,
        "optimizer": "Adam",
        "learning_rate": lr,
        "initialization_scale": init_scale,
        "steps": steps,
        "best_loss": best_loss,
        "near_exact_tolerances": near_exact_tolerances,
        "primary_tolerance": primary_tolerance,
        "near_exact_pairs_primary": near_exact_summary["num_near_exact_pairs"],
        "unitarity_residual_max": unitarity_residuals["max_unitarity_residual"],
        "generator_norm_max_best_iterate": generator_norms["max_generator_norm"],
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "timestamp_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_elapsed_seconds": elapsed_total,
    }
    
    return {
        "best_bases": best_bases,
        "pairwise_overlaps": pairwise_overlaps,
        "pairwise_diagnostics": pairwise_diagnostics,
        "unitarity_residuals": unitarity_residuals,
        "generator_norms": generator_norms,
        "optimization_history": history,
        "metadata": metadata,
    }
