#!/bin/bash

python setup.py install --user
pytest tests/spinnaker_tests/test_spinnaker_iaf_psc_exp.py
./stash/copy_generated_models.sh
(cd /home/siirty/Projects/nestml-spinnaker-models/ ; python setup.py develop ; python examples/my_example.py)
