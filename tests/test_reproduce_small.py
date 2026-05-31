import pytest
import shutil
from pathlib import Path
import sys

# Ensure src/ is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.amub.config import AMUBConfig
from src.amub.experiment import run_single_experiment
from src.amub.io_utils import make_run_dir, save_run_artifacts

def test_integration_reproduce_small():
    # Setup configuration dictionary for a small, fast run
    config_dict = {
        "dimension": 3,
        "n_bases": 2,
        "dtype": "complex128",
        "seed": 99,
        "initialization_scale": 0.05,
        "learning_rate": 0.02,
        "steps": 10,  # 10 steps is extremely fast
        "log_interval": 2,
        "matrix_exp_backend": "torch_native",
        "backend": "cpu",
        "near_exact_tolerances": [1.0e-6],
        "primary_tolerance": 1.0e-6,
        "output_root": "results/runs_test_temp"
    }
    
    config = AMUBConfig(config_dict)
    
    # Run the experiment
    result = run_single_experiment(config)
    
    assert "best_bases" in result
    assert "pairwise_overlaps" in result
    assert "pairwise_diagnostics" in result
    assert "unitarity_residuals" in result
    assert "optimization_history" in result
    assert "metadata" in result
    
    # Assert run directory constructs correctly
    output_root = Path(config_dict["output_root"])
    run_dir = make_run_dir(output_root, 3, 2, "complex128", 99)
    assert run_dir.exists()
    
    # Save artifacts
    save_run_artifacts(result, run_dir)
    
    # Assert all required TOMS output files are written to disk
    assert (run_dir / "best_bases.npy").exists()
    assert (run_dir / "pairwise_overlaps.npz").exists()
    assert (run_dir / "pairwise_diagnostics.json").exists()
    assert (run_dir / "unitarity_residuals.json").exists()
    assert (run_dir / "generator_norms.json").exists()
    assert (run_dir / "optimization_history.csv").exists()
    assert (run_dir / "run_metadata.json").exists()
    
    # Cleanup temporary run artifacts
    shutil.rmtree(output_root, ignore_errors=True)
