#!/bin/bash -x

ml Stages/2024 GCC Boost ParaStationMPI GSL jemalloc Python SciPy-Stack mpi4py CMake Autotools

python3 -m pip install pytest-xdist pytest-timeout junitparser

cd
mv -vi nest-simulator /tmp
git clone https://github.com/nest/nest-simulator
cd nest-simulator
git checkout v3.6
cd ..

mv -vi nest-simulator-build /tmp/
mkdir nest-simulator-build
cd nest-simulator-build

# TODO: -Dwith-detailed-timers=ON required?
cmake -DCMAKE_INSTALL_PREFIX:PATH=$HOME/nest-simulator-install -Dwith-mpi=ON -Dwith-optimize="-O3" -Dwith-readline=OFF ../nest-simulator

make -j16
make install
