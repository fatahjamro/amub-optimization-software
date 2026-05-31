#!/usr/bin/env bash
set -e

echo "=========================================="
echo "Starting Full ACM TOMS Paper Reproduction"
echo "=========================================="

# 1. Run full mathematical correctness tests
python3 -m pytest tests/

# 2. Run single-seed sweep (n = 2 to 7, complex128)
python3 scripts/run_single_seed_sweep.py --config configs/single_seed_sweep.yaml

# 3. Run precision sensitivity campaigns
python3 scripts/run_precision_campaign.py \
  --config128 configs/multiseed_complex128.yaml \
  --config64 configs/multiseed_complex64.yaml

# 4. Run extended campaign (20 seeds, n = 6, complex128)
python3 scripts/run_multiseed_campaign.py --config configs/n6_20seed_complex128.yaml

# 5. Summarize campaigns
python3 scripts/summarize_results.py --results-root results/runs

# 6. Generate paper figures
python3 scripts/generate_figures.py --summary-root results/summaries --output-root results

echo ""
echo "=========================================="
echo "Full paper reproduction completed successfully!"
echo "All summaries and PDF figures are ready."
echo "=========================================="
