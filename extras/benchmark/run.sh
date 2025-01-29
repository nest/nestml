#!/bin/bash

ml Stages/2024 GCC Boost ParaStationMPI GSL jemalloc Python SciPy-Stack mpi4py CMake Autotools

cd Running
python3 benchmark.py
cd ..
