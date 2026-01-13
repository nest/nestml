# -*- coding: utf-8 -*-
#
# test_synapse_continuous_third_factor_is_postsynaptic_inline_expression.py
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


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapseContinuousThirdFactorIsPostsynapticInlineExpression:
    r"""Test that synapses with a third-factor continuous-time input port can successfully grab the values from the postsynaptic neuron if the port is connected to a postsynaptic inline expression (n.b. as apart from a postsynaptic state variable)"""

    neuron_model_name = "continuous_post_synaptic_third_factor_neuron"
    synapse_model_name = "continuous_post_synaptic_third_factor_synapse"

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        r"""Generate the model code"""
        files = [os.path.join("tests", "nest_tests", "resources", self.neuron_model_name + ".nestml"),
                 os.path.join("tests", "nest_tests", "resources", self.synapse_model_name + ".nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]

        generate_nest_target(
            input_path=input_path,
            target_path="target_clapp",
            module_name="nestmlmodule",
            logging_level="DEBUG",
            suffix="_nestml",
            codegen_opts={
                "neuron_parent_class": "StructuralPlasticityNode",
                "neuron_parent_class_include": "structural_plasticity_node.h",
                "neuron_synapse_pairs": [{
                    "neuron": self.neuron_model_name,
                    "synapse": self.synapse_model_name,
                    "post_ports": ["post_spikes", ("I_AMPA", "I_AMPA")],
                }],
                "weight_variable": {self.synapse_model_name: "w"},
                "continuous_state_buffering_method": "post_spike_based"
            }
        )

    def test_nest_stdp_synapse(self):
        pre_spike_times = np.linspace(100., 500., 15)
        on_spike_times = [200.]
        off_spike_times = [400.]
        post_spike_times = pre_spike_times

        nest.ResetKernel()
        nest.resolution = 1.
        nest.set_verbosity("M_ERROR")

        nest.Install("nestmlmodule")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times,
                                     "allow_offgrid_times": True})
        pre_sg_on = nest.Create("spike_generator",
                                params={"spike_times": on_spike_times,
                                        "allow_offgrid_times": True})
        pre_sg_off = nest.Create("spike_generator",
                                 params={"spike_times": off_spike_times,
                                         "allow_offgrid_times": True})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(self.neuron_model_name + "_nestml__with_" + self.synapse_model_name + "_nestml")

        receptor_types = nest.GetStatus(post_neuron, "receptor_types")[0]

        nest.Connect(pre_sg, pre_neuron, syn_spec={"weight": 1.})
        nest.Connect(pre_sg_on, post_neuron, syn_spec={"weight": 9999., "receptor_type": receptor_types["SPIKES_ON"]})
        nest.Connect(pre_sg_off, post_neuron, syn_spec={"weight": 9999., "receptor_type": receptor_types["SPIKES_OFF"]})
        nest.Connect(post_sg, post_neuron, syn_spec={"weight": 0., "receptor_type": receptor_types["SPIKES_AMPA"]})

        sr_pre = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, sr_pre)

        sr_post = nest.Create("spike_recorder")
        nest.Connect(post_neuron, sr_post)

        mm = nest.Create("multimeter", params={"record_from": ["x", "I_AMPA"]})
        nest.Connect(mm, post_neuron)

        syn_opts = {"synapse_model": self.synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml"}

        nest.Connect(pre_neuron, post_neuron, syn_spec=syn_opts | {"receptor_type": receptor_types["SPIKES_AMPA"]})
        syn = nest.GetConnections(source=pre_neuron, synapse_model=self.synapse_model_name + "_nestml__with_" + self.neuron_model_name + "_nestml")
        assert len(syn) == 1

        T_sim = 100. + max(np.amax(pre_spike_times), np.amax(post_spike_times))  # [ms]
        # instead of calling ``nest.Simulate(T_sim)``, simulate in small increments
        sim_interval = nest.resolution    # [ms]
        timevec = [0.]
        w = [syn[0].get("w")]
        while nest.biological_time < T_sim:
            nest.Simulate(sim_interval)
            timevec.append(nest.biological_time)
            w.append(syn[0].get("w"))

        #
        #    plot the simulation results
        #

        timevec_mm = mm.events["times"]
        x = mm.events["x"]
        I_AMPA = mm.events["I_AMPA"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=5)

            ax[0].scatter(sr_pre.get("events")["times"], np.zeros_like(sr_pre.get("events")["times"]))
            ax[0].set_ylabel("Pre spikes")

            ax[1].scatter(sr_post.get("events")["times"], np.zeros_like(sr_post.get("events")["times"]))
            ax[1].set_ylabel("Post spikes")

            ax[2].plot(timevec_mm, x, label="x")
            ax[2].set_ylabel("Neuron x")
            ax[3].plot(timevec_mm, I_AMPA)
            ax[3].set_ylabel("Neuron I_AMPA")
            ax[4].plot(timevec, w, color="orange")
            ax[4].set_ylabel("Synapse w")
            for _ax in ax:
                _ax.grid()
                if not _ax == ax[-1]:
                    _ax.set_xticklabels([])
                _ax.set_xlim(0, np.amax(timevec))

            fig.savefig("test_synapse_continuous_third_factor_is_postsynaptic_inline_expression.png")

        #
        #    check for correct value, based on running this test once and hard-coding the value
        #

        np.testing.assert_allclose(w[-1], 6.697220578)
