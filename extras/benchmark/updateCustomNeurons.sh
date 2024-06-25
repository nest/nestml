#!/bin/bash
source ../nest-simulator-install/bin/nest_vars.sh


cd Running/targets_iaf_psc_exp/target_optimized
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..

cd Running/targets_iaf_psc_exp/target
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..

cd Running/targets_iaf_psc_exp/target_plastic
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..

cd Running/targets_aeif_psc_alpha/target_optimized
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..

cd Running/targets_aeif_psc_alpha/target
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..

cd Running/targets_aeif_psc_alpha/target_plastic
rm -rf CMakeCache.txt CMakeFiles
cmake .
make -j24 install
cd ../..
