#!/usr/bin/env bash
#SBATCH --job-name=amub-jan-64-arr
#SBATCH --partition=defq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4GB
#SBATCH --time=02:00:00
#SBATCH --array=0-9
#SBATCH --output=results/amub_janus_64_arr_%A_%a.log
#SBATCH --error=results/amub_janus_64_arr_%A_%a.err

set -e

# Calculate seed range for this array task index
START_SEED=$((SLURM_ARRAY_TASK_ID * 10))
END_SEED=$((START_SEED + 9))
SEEDS=$(seq -s ' ' $START_SEED $END_SEED)

echo "================================================================="
echo "Starting AMUB 10-Seed complex64 Campaign (Array Task $SLURM_ARRAY_TASK_ID) on JANUS"
echo "Job ID: $SLURM_JOB_ID (Array Job ID: $SLURM_ARRAY_JOB_ID, Task ID: $SLURM_ARRAY_TASK_ID)"
echo "Running on Node: $SLURM_NODENAME"
echo "Seeds: $SEEDS"
echo "Start Time: $(date)"
echo "================================================================="

mkdir -p results

if command -v module &> /dev/null; then
    module load python3 || module load anaconda || module load python || echo "No module command matched."
fi

echo "Activating virtualenv..."
source venv/bin/activate || echo "Failed to activate venv, using system python."

echo "Executing complex64 campaign runner for seeds $SEEDS..."
python3 scripts/run_multiseed_campaign.py --config configs/multiseed_janus_64.yaml --seeds $SEEDS

echo "================================================================="
echo "Array Task $SLURM_ARRAY_TASK_ID completed at $(date)!"
echo "================================================================="
