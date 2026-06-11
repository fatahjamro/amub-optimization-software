#!/usr/bin/env bash
#SBATCH --job-name=amub-janus-64
#SBATCH --partition=defq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8GB
#SBATCH --time=12:00:00
#SBATCH --output=results/amub_janus_64_%j.log
#SBATCH --error=results/amub_janus_64_%j.err

set -e

echo "================================================================="
echo "Starting AMUB 100-Seed complex64 Campaign on JANUS HPC"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on Node: $SLURM_NODENAME"
echo "Start Time: $(date)"
echo "================================================================="

mkdir -p results

if command -v module &> /dev/null; then
    module load python3 || module load anaconda || module load python || echo "No module command matched."
fi

echo "Activating virtualenv..."
source venv/bin/activate || echo "Failed to activate venv, using system python."

echo "Executing complex64 campaign runner..."
python3 scripts/run_multiseed_campaign.py --config configs/multiseed_janus_64.yaml

echo "Summarizing results..."
python3 scripts/summarize_results.py --results-root results/runs

echo "================================================================="
echo "Campaign successfully completed at $(date)!"
echo "================================================================="
