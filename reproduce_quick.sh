#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Running ACM TOMS Smoke Test & PyTest Suite"
echo "=========================================="

# 1. Run mathematical verification and integration tests
python3 -m pytest tests/

# 2. Run quick single-seed sweep (3 and 4 bases, 50 steps)
python3 scripts/run_single_seed_sweep.py --config configs/single_seed_sweep.yaml --quick

# 3. Summarize and aggregate results
python3 scripts/summarize_results.py --results-root results/runs

# 4. Generate all vector PDF figures
python3 scripts/generate_figures.py --summary-root results/summaries --output-root results --quick

echo ""
echo "=========================================="
echo "Smoke test completed successfully!"
echo "=========================================="
