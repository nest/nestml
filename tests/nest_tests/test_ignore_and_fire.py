# -*- coding: utf-8 -*-
#
# test_ignore_and_fire.py
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
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


class TestIgnoreAndFire:

    neuron_model_name = "ignore_and_fire_neuron_nestml__with_stdp_synapse_nestml"
    synapse_model_name = "stdp_synapse_nestml__with_ignore_and_fire_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "ignore_and_fire_neuron",
                                                  "synapse": "stdp_synapse",
                                                  "post_ports": ["post_spikes"]}]}

        files = [os.path.join("models", "neurons", "ignore_and_fire_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)
        nest.Install("nestmlmodule")

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    @pytest.mark.parametrize("resolution", [1., .1])
    def test_ignore_and_fire_with_stdp(self, resolution: float):
        sim_time = 1001.   # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        pre_neuron = nest.Create(self.neuron_model_name)
        post_neuron = nest.Create(self.neuron_model_name)
        pre_neuron.firing_rate = 10.
        pre_neuron.phase_steps = 50
        post_neuron.firing_rate = 100.
        post_neuron.phase_steps = 5
        pre_sr = nest.Create("spike_recorder")
        post_sr = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, pre_sr)
        nest.Connect(post_neuron, post_sr)

        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": self.synapse_model_name})

        # split the simulation in two to ensure continuity in state between the two halves
        nest.Simulate(sim_time // 2)
        nest.Simulate(sim_time - (sim_time // 2))

        n_ev_pre = len(pre_sr.get("events")["times"])
        n_ev_post = len(post_sr.get("events")["times"])

        assert n_ev_pre == pre_neuron.firing_rate
        assert n_ev_post == post_neuron.firing_rate
