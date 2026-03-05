# -*- coding: utf-8 -*-
#
# test_neuron_with_multiple_different_plastic_synapses.py
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

sim_mdl = True
sim_ref = True


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNeuronWithMultipleDifferentSynapses:
    r"""Test that code can be generated when a postsynaptic neuron is connected to by several different synapse models"""
    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stdp_nn_symm_synapse_nestml_and_stdp_nn_restr_symm_synapse_nestml"
    synapse1_model_name = "stdp_nn_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"
    synapse2_model_name = "stdp_nn_restr_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_nn_symm_synapse.nestml"),
                 os.path.join("models", "synapses", "stdp_nn_restr_symm_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapses": {"stdp_nn_symm_synapse": {"post_ports": ["post_spikes"]},
                                                                                  "stdp_nn_restr_symm_synapse": {"post_ports": ["post_spikes"]}}}],
                                           "delay_variable": {"stdp_nn_symm_synapse": "d",
                                                              "stdp_nn_restr_symm_synapse": "d"},
                                           "weight_variable": {"stdp_nn_symm_synapse": "w",
                                                               "stdp_nn_restr_symm_synapse": "w"}})

    def test_stdp_nn_synapse(self):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        post_neuron = nest.Create(TestNeuronWithMultipleDifferentSynapses.neuron_model_name)
        pre_neuron1 = nest.Create("parrot_neuron")
        pre_neuron2 = nest.Create("parrot_neuron")

        nest.Connect(pre_neuron1, post_neuron, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse1_model_name})
        nest.Connect(pre_neuron2, post_neuron, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse2_model_name})

        # Helper to read the single connection weight between a given pre and the post neuron
        def read_weight(pre, post):
            conns = nest.GetConnections(source=pre, target=post)
            if len(conns) == 0:
                return None
            return nest.GetStatus(conns, "weight")[0]

        # Run two independent experiments: only pre_neuron1 active, then only pre_neuron2 active.
        sim_time = 1000.0  # ms
        pre_rate = 100.0  # Hz, strong enough to drive plasticity
        post_rate = 50.0  # Hz background to make the post neuron spike

        # Experiment A: only pre_neuron1 fires
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")
        post = nest.Create(TestNeuronWithMultipleDifferentSynapses.neuron_model_name)
        p1 = nest.Create("parrot_neuron")
        p2 = nest.Create("parrot_neuron")
        nest.Connect(p1, post, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse1_model_name})
        nest.Connect(p2, post, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse2_model_name})

        # Create spike recorders for Experiment A
        sr_p1_A = nest.Create("spike_recorder")
        sr_p2_A = nest.Create("spike_recorder")
        sr_post_A = nest.Create("spike_recorder")
        nest.Connect(p1, sr_p1_A)
        nest.Connect(p2, sr_p2_A)
        nest.Connect(post, sr_post_A)

        # Poisson generator to drive pre_neuron1 only
        pg_pre1 = nest.Create("poisson_generator", params={"rate": pre_rate, "start": 0.0, "stop": sim_time})
        nest.Connect(pg_pre1, p1, syn_spec={"weight": 1.0, "delay": 1.0})

        # Background drive to make post neuron spike
        pg_post = nest.Create("poisson_generator", params={"rate": post_rate, "start": 0.0, "stop": sim_time})
        nest.Connect(pg_post, post, syn_spec={"weight": 10000.0, "delay": 1.0})

        # Read initial weights
        w1_before = read_weight(p1, post)
        w2_before = read_weight(p2, post)

        nest.Simulate(sim_time)

        w1_after_A = read_weight(p1, post)
        w2_after_A = read_weight(p2, post)

        # Plot Experiment A
        if TEST_PLOTS:
            self._plot_raster("Experiment A: pre_neuron1 active", sr_p1_A, sr_p2_A, sr_post_A)

        # Expectation: only connection from pre_neuron1 changes
        assert w1_before is not None and w1_after_A is not None
        assert w2_before is not None and w2_after_A is not None
        assert abs(w1_after_A - w1_before) > 1e-6, "weight for pre_neuron1 should have changed"
        assert abs(w2_after_A - w2_before) < 1e-6, "weight for pre_neuron2 should NOT have changed"

        # Experiment B: only pre_neuron2 fires
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")
        post = nest.Create(TestNeuronWithMultipleDifferentSynapses.neuron_model_name)
        p1 = nest.Create("parrot_neuron")
        p2 = nest.Create("parrot_neuron")
        nest.Connect(p1, post, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse1_model_name})
        nest.Connect(p2, post, syn_spec={"synapse_model": TestNeuronWithMultipleDifferentSynapses.synapse2_model_name})

        # Create spike recorders for Experiment B
        sr_p1_B = nest.Create("spike_recorder")
        sr_p2_B = nest.Create("spike_recorder")
        sr_post_B = nest.Create("spike_recorder")
        nest.Connect(p1, sr_p1_B)
        nest.Connect(p2, sr_p2_B)
        nest.Connect(post, sr_post_B)

        # Poisson generator to drive pre_neuron2 only
        pg_pre2 = nest.Create("poisson_generator", params={"rate": pre_rate, "start": 0.0, "stop": sim_time})
        nest.Connect(pg_pre2, p2, syn_spec={"weight": 1.0, "delay": 1.0})

        # Background drive to make post neuron spike
        pg_post = nest.Create("poisson_generator", params={"rate": post_rate, "start": 0.0, "stop": sim_time})
        nest.Connect(pg_post, post, syn_spec={"weight": 10000.0, "delay": 1.0})

        # Read initial weights
        w1_before = read_weight(p1, post)
        w2_before = read_weight(p2, post)

        nest.Simulate(sim_time)

        w1_after_B = read_weight(p1, post)
        w2_after_B = read_weight(p2, post)

        # Plot Experiment B
        if TEST_PLOTS:
            self._plot_raster("Experiment B: pre_neuron2 active", sr_p1_B, sr_p2_B, sr_post_B)

        # Expectation: only connection from pre_neuron2 changes
        assert w1_before is not None and w1_after_B is not None
        assert w2_before is not None and w2_after_B is not None
        assert abs(w2_after_B - w2_before) > 1e-6, "weight for pre_neuron2 should have changed"
        assert abs(w1_after_B - w1_before) < 1e-6, "weight for pre_neuron1 should NOT have changed"

    def _plot_raster(self, title, sr_p1, sr_p2, sr_post):
        """Helper function to plot spike raster"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Get spike data
        data_p1 = nest.GetStatus(sr_p1, "events")[0]
        data_p2 = nest.GetStatus(sr_p2, "events")[0]
        data_post = nest.GetStatus(sr_post, "events")[0]

        # Plot spikes
        ax.scatter(data_p1["times"], np.ones(len(data_p1["times"])), c="blue", label="p1", s=20)
        ax.scatter(data_p2["times"], 2 * np.ones(len(data_p2["times"])), c="green", label="p2", s=20)
        ax.scatter(data_post["times"], 3 * np.ones(len(data_post["times"])), c="red", label="post", s=20)

        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["p1", "p2", "post"])
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Neuron")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("/tmp/raster_" + title.replace(" ", "_").replace(":", "") + ".png")
        plt.close()
