#!/bin/bash

# This bash script compiles the generated code in different target directories.
# Each directory contains a combination of neuron with or without a synapse model generated from NESTML.

source ../nest-simulator-install/bin/nest_vars.sh

cd Running/targets_aeif_psc_alpha/target_optimized
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../../..

cd Running/targets_aeif_psc_alpha/target
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../../..

cd Running/targets_aeif_psc_alpha/target_plastic
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../../..


cd Running/targets_aeif_psc_alpha/target_plastic_noco
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../../..
