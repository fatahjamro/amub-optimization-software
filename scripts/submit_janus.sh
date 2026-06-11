#!/usr/bin/env bash
#SBATCH --job-name=amub-janus
#SBATCH --partition=defq        # Use the standard compute partition (change to 'gpu' if running GPU backend)
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4          # Allocate 4 CPU cores
#SBATCH --mem=8GB                  # Memory allocation
#SBATCH --time=12:00:00            # Wall-time limit (HH:MM:SS)
#SBATCH --output=results/amub_janus_%j.log
#SBATCH --error=results/amub_janus_%j.err

# Exit immediately if a command exits with a non-zero status
set -e

echo "================================================================="
echo "Starting AMUB 100-Seed Optimization Campaign on JANUS HPC"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on Node: $SLURM_NODENAME"
echo "Start Time: $(date)"
echo "================================================================="

# Create results output directory if it doesn't exist
mkdir -p results

# 1. Load Anaconda or Python environment modules
# Adjust module names to match JANUS environment specifics if necessary
if command -v module &> /dev/null; then
    echo "Loading conda/python module..."
    module load anaconda || module load python || echo "No module command matched, proceeding with path defaults."
fi

# 2. Activate Python Virtual Environment
echo "Activating virtualenv..."
source venv/bin/activate || echo "Failed to activate venv, using system python."

# 3. Run the Multi-Seed Campaigns
echo "Executing complex128 campaign runner..."
python3 scripts/run_multiseed_campaign.py --config configs/multiseed_janus_100.yaml

echo "Executing complex64 campaign runner..."
python3 scripts/run_multiseed_campaign.py --config configs/multiseed_janus_64.yaml

# 4. Compile and Summarize Results
echo "Summarizing results..."
python3 scripts/summarize_results.py --results-root results/runs

echo "================================================================="
echo "Campaign successfully completed at $(date)!"
echo "================================================================="
