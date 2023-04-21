#!/bin/bash

SRC_DIR=/home/siirty/Projects/nestml/spinnaker-install/
DST_DIR=/home/siirty/Projects/nestml-spinnaker-models/

cp -f $SRC_DIR/python_models8/model_binaries/* $DST_DIR/python_models8/model_binaries/
cp -f $SRC_DIR/python_models8/neuron/builds/* $DST_DIR/python_models8/neuron/builds/
cp -f $SRC_DIR/python_models8/neuron/implementations/* $DST_DIR/python_models8/neuron/implementations/