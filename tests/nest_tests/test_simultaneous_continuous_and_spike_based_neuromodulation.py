# -*- coding: utf-8 -*-
#
# test_simultaneous_continuous_and_spike_based_neuromodulation.py
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
class TestSimultaneousContinuousAndSpikeBasedNeuromodulation:
    r"""
    Test that a combination of continuous-time-based and spike-based neuromodulation in a synapse compiles.
    """

    neuron_model_name = "iaf_psc_exp_nonlineardendrite_neuron_nestml__with_continuous_and_spike_based_neuromodulated_stdp_synapse_nestml"
    synapse_model_name = "continuous_and_spike_based_neuromodulated_stdp_synapse_nestml__with_iaf_psc_exp_nonlineardendrite_neuron_nestml"

    @pytest.fixture(scope="class", autouse=True)
    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("doc", "tutorials", "sequence_learning", "iaf_psc_exp_nonlineardendrite_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "continuous_and_spike_based_neuromodulated_stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_nonlineardendrite_neuron",
                                                                     "synapse": "continuous_and_spike_based_neuromodulated_stdp_synapse",
                                                                     "post_ports": ["post_spikes", ("dAP_trace", "dAP_trace")],
                                                                     "vt_ports": ["mod_spikes"]}],
                                           "continuous_state_buffering_method": "post_spike_based",
                                           "delay_variable": {"continuous_and_spike_based_neuromodulated_stdp_synapse": "d"},
                                           "weight_variable": {"continuous_and_spike_based_neuromodulated_stdp_synapse": "w"}})

    def test_nest_stdp_synapse(self):
        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        vt_spike_times = [4.]    # must be early to gate pre/post plasticity on [ms]

        for nonzero_dAP_trace in [True, False]:
            t_hist, w_hist = self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                                                synapse_model_name=self.synapse_model_name,
                                                resolution=.1,  # [ms]
                                                delay=1.,  # [ms]
                                                pre_spike_times=pre_spike_times,
                                                post_spike_times=post_spike_times,
                                                vt_spike_times=vt_spike_times,
                                                nonzero_dAP_trace=nonzero_dAP_trace,
                                                fname_snip=fname_snip)
            if nonzero_dAP_trace:
                assert np.abs(w_hist[-1] - w_hist[0]) > 1E-3, "Weights should change under this protocol!"
            else:
                np.testing.assert_allclose(w_hist[-1], w_hist[0]), "Weights should not change under this protocol!"

    def run_synapse_test(self, neuron_model_name,
                         synapse_model_name,
                         resolution=1.,  # [ms]
                         delay=1.,  # [ms]
                         sim_time=None,  # if None, computed from pre and post spike times
                         pre_spike_times=None,
                         post_spike_times=None,
                         vt_spike_times=None,
                         nonzero_dAP_trace=True,
                         fname_snip=""):

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if vt_spike_times is None:
            vt_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times, initial=0.), np.amax(
                post_spike_times, initial=0.), np.amax(vt_spike_times, initial=0.)) + 5 * delay

        nest.ResetKernel()
        nest.set_verbosity("M_ERROR")
        nest.SetKernelStatus({"resolution": resolution})
        nest.Install("nestmlmodule")

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))
        print("VT spike times: " + str(vt_spike_times))

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})
        vt_sg = nest.Create("spike_generator",
                            params={"spike_times": vt_spike_times,
                                    "allow_offgrid_times": True})

        # create  volume transmitter
        vt = nest.Create("volume_transmitter")
        vt_parrot = nest.Create("parrot_neuron")
        nest.Connect(vt_sg, vt_parrot)
        nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                              "weight": 1.,
                                              "delay": 1.})   # delay is ignored?!

        # set up custom synapse models
        wr = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": delay, "receptor_type": 0,
                        "volume_transmitter": vt})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)
        if nonzero_dAP_trace:
            post_neuron.dAP_trace = 1.
            post_neuron.evolve_dAP_trace = 0.

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        spikedet_vt = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": ["V_m", "post_tr__for_continuous_and_spike_based_neuromodulated_stdp_synapse_nestml"]})

        receptor_types = nest.GetStatus(post_neuron, "receptor_types")[0]

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999., "receptor_type": receptor_types["I_1"]})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "stdp_nestml_rec", "receptor_type": receptor_types["I_2"]})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)
        nest.Connect(vt_parrot, spikedet_vt)

        # get STDP synapse and weight before protocol
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

        t = 0.
        t_hist = []
        w_hist = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            w_hist.append(nest.GetStatus(syn)[0]["w"])

        return t_hist, w_hist
