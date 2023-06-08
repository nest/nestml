#!/bin/bash

(cd /home/nestml/spinnaker-install/c_models; make clean; make)
cp /home/nestml/spinnaker-install/python_models8/model_binaries/* /home/nestml-spinnaker-models/python_models8/model_binaries/
python /home/nestml-spinnaker-models/examples/my_example.py
