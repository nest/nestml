#!/bin/bash
#SBATCH --account=slns
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=dc-gpu
#SBATCH --gres=gpu:1
#SBATCH --output=run_simulation_%j.out
#SBATCH --error=run_simulation_%j.err
# *** start of job script ***
# Note: The current working directory at this point is
# the directory where sbatch was executed.

ml Stages/2022 GCC OpenMPI CUDA GSL Python SciPy-Stack mpi4py CMake Autotools

# Path to nestgpu_vars.sh
nestgpu_vars=/p/project/cslns/babu1/nest-gpu-install/bin/nestgpu_vars.sh

# Path to python script
script=/p/project/cslns/babu1/nest-gpu/example_iaf_psc_exp.py

source $nestgpu_vars

export NUMEXPR_MAX_THREADS=128
export OMP_DISPLAY_ENV=VERBOSE
export OMP_DISPLAY_AFFINITY=TRUE
export OMP_PROC_BIND=TRUE

export OMP_NUM_THREADS=2

# Bind by threads
srun --cpus-per-task=2 --threads-per-core=1 --cpu-bind=verbose,threads --distribution=block:cyclic:fcyclic python3 $script

