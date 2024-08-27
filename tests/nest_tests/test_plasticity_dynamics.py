# -*- coding: utf-8 -*-
#
# test_plasticity_dynamics.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import logging
import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


@pytest.fixture(autouse=True,
                scope="module")
def nestml_generate_target():
    r"""Generate the neuron model code"""
    files = [os.path.join("tests", "nest_tests", "resources", "test_plasticity_dynamics_neuron.nestml"),
             os.path.join("tests", "nest_tests", "resources", "test_plasticity_dynamics_synapse.nestml")]
    input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
        os.pardir, os.pardir, s))) for s in files]
    generate_nest_target(input_path=input_path,
                         logging_level="DEBUG",
                         suffix="_nestml",
                         codegen_opts={"neuron_synapse_pairs": [{"neuron": "test_plasticity_dynamics_neuron",
                                                                 "synapse": "test_plasticity_dynamics_synapse",
                                                                 "post_ports": ["post_spikes"]}],
                                       "delay_variable": {"test_plasticity_dynamics_synapse": "d"},
                                       "weight_variable": {"test_plasticity_dynamics_synapse": "w"}})


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
def test_plasticity_dynamics():
    r"""Test that the time interval-based plasticity rule in ``test_plasticity_dynamics_synapse`` is implemented correctly on a simple sequences of spikes"""
    nest.ResetKernel()
    nest.resolution = .01
    nest.Install("nestmlmodule")

    pre_spikes = nest.Create('spike_train_injector', params={'spike_times': [1., 10.]})
    post_driver_spikes = nest.Create('spike_train_injector', params={'spike_times': [1., 5., 8.]})
    neuron = nest.Create('test_plasticity_dynamics_neuron_nestml__with_test_plasticity_dynamics_synapse_nestml')
    sr = nest.Create('spike_recorder')
    wr = nest.Create('weight_recorder')
    nest.SetDefaults('test_plasticity_dynamics_synapse_nestml__with_test_plasticity_dynamics_neuron_nestml', {'weight_recorder': wr})
    rec_types = nest.GetDefaults('test_plasticity_dynamics_neuron_nestml__with_test_plasticity_dynamics_synapse_nestml')['receptor_types']

    # Create plastic synapse with pre_spikes as presynaptic neuron
    nest.Connect(pre_spikes, neuron,
                 syn_spec={'synapse_model': 'test_plasticity_dynamics_synapse_nestml__with_test_plasticity_dynamics_neuron_nestml',
                           'receptor_type': rec_types['SPIKES_PLASTIC']})

    # Add connection from post_driver_spikes to elicit spikes in postsynaptic neuron without triggering
    # plasticity mechanism. Note that neuron will spike 1 ms later than the times set in post_driver_spikes
    nest.Connect(post_driver_spikes, neuron,
                 syn_spec={'synapse_model': 'static_synapse',
                           'receptor_type': rec_types['SPIKES_PARROT']})

    nest.Connect(neuron, sr)
    nest.Simulate(15)

    print("Spike times of presynaptic neuron :", pre_spikes.spike_times)
    print("Spike times of postsynaptic neuron:", sr.events['times'])
    print(wr.events)
    syn = nest.GetConnections(pre_spikes, neuron)
    print(syn.get())

    # the actual test
    np.testing.assert_almost_equal(actual=syn.get("w"),
                                   desired=1.01)
