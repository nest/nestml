#!/bin/bash

# need to create this directory first, otherwise it gets ignored in the PYTHONPATH!
mkdir $HOME/nestml/spinnaker-install

PYTHONPATH=$HOME/nestml/spinnaker-install:$HOME/spinnaker/SpiNNMachine:$HOME/spinnaker/DataSpecification:/usr/local/lib/python3.10/site-packages python3 -m pytest -s --pdb ./tests/spinnaker_tests/test_spinnaker_iaf_psc_exp.py

