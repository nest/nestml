# -*- coding: utf-8 -*-
#
# test_priority_neuron.py
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

import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


class TestNeuronPriority:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""
        files = [os.path.join("tests", "resources", "neuron_event_priority_test.nestml"),
                 os.path.join("tests", "resources", "neuron_event_inv_priority_test.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestml_module",
                             suffix="_nestml")
        try:
            nest.Install("nestml_module")
        except Exception:
            pass

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_neuron_event_priority(self):
        resolution = .5    # [ms]

        # one additional pre spike to ensure processing of post spikes in the intermediate interval
        port1_spike_times = np.array([1.])
        port2_spike_times = np.array([1.])

        neuron_model_name = "event_priority_test_neuron_nestml"
        tr = self.run_nest_simulation(neuron_model_name=neuron_model_name,
                                      resolution=resolution,
                                      port1_spike_times=port1_spike_times,
                                      port2_spike_times=port2_spike_times)

        neuron_model_name = "event_inv_priority_test_neuron_nestml"
        tr_inv = self.run_nest_simulation(neuron_model_name=neuron_model_name,
                                          resolution=resolution,
                                          port1_spike_times=port1_spike_times,
                                          port2_spike_times=port2_spike_times)

        np.testing.assert_allclose(tr, 4.14159)
        np.testing.assert_allclose(tr_inv, 6.28318)

    def run_nest_simulation(self, neuron_model_name,
                            resolution=1.,  # [ms]
                            port1_spike_times=None,
                            port2_spike_times=None):

        if port1_spike_times is None:
            port1_spike_times = []

        if port2_spike_times is None:
            port2_spike_times = []

        sim_time = max(np.amax(port1_spike_times), np.amax(port2_spike_times)) + 10.

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.SetKernelStatus({'resolution': resolution})

        # create spike_generators with these times
        port1_sg = nest.Create("spike_generator",
                               params={"spike_times": port1_spike_times})
        port2_sg = nest.Create("spike_generator",
                               params={"spike_times": port2_spike_times})

        # create parrot neurons and connect spike_generators
        neuron = nest.Create(neuron_model_name)
        sr = nest.Create("spike_recorder")

        nest.Connect(port1_sg, neuron, "one_to_one", syn_spec={"receptor_type": 1, "delay": 1.})
        nest.Connect(port2_sg, neuron, "one_to_one", syn_spec={"receptor_type": 2, "delay": 1.})
        nest.Connect(neuron, sr)

        nest.Simulate(sim_time)

        return neuron.tr
