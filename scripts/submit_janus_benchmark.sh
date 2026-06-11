#!/usr/bin/env bash
#SBATCH --job-name=amub-benchmark
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16GB
#SBATCH --time=01:00:00
#SBATCH --output=results/amub_benchmark_%j.log
#SBATCH --error=results/amub_benchmark_%j.err

set -e

echo "================================================================="
echo "Starting AMUB Hardware Benchmarks on JANUS GPU Node"
echo "Job ID: $SLURM_JOB_ID"
echo "Running on Node: $SLURM_NODENAME"
echo "Start Time: $(date)"
echo "================================================================="

mkdir -p results

if command -v module &> /dev/null; then
    module load python3 || module load anaconda || module load python || echo "No module command matched."
    module load cuda || echo "No CUDA module matched."
fi

echo "Activating virtualenv..."
source venv/bin/activate || echo "Failed to activate venv, using system python."

echo "Running hardware benchmarks script..."
python3 scripts/run_hardware_benchmarks.py

echo "================================================================="
echo "Benchmarks completed at $(date)!"
echo "================================================================="
