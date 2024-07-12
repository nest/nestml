#!/bin/bash
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
