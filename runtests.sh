#!/bin/bash
#LD_LIBRARY_PATH=/home/archels/nestml-fork-jit/nestml:/home/archels/nest-simulator-build/lib/nest:/home/archels/nestml-fork-jit/nestml/target PYTHONPATH=$PYTHONPATH:/home/archels/ode-toolbox:/home/archels/nest-simulator-build/lib/python3.5/site-packages ipython3 -m pytest -- -s --pdb tests/nest_tests/stdp_synapse_test.py
LD_LIBRARY_PATH=/home/archels/nestml-fork-jit/nestml:/home/archels/nest-simulator-build/lib/nest:/tmp/nestml-stdp PYTHONPATH=$PYTHONPATH:/home/archels/ode-toolbox:/home/archels/nest-simulator-build/lib/python3.5/site-packages ipython3 -m pytest -- -s --pdb tests/nest_tests/stdp_synapse_test.py

