#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=24:00:00
#export OMP_NUM_THREADS = 128

cd $PWD
mpirun -np 32 python3 jezebel.py
