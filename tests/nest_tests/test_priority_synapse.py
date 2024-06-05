# -*- coding: utf-8 -*-
#
# test_priority_synapse.py
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


class TestSynapsePriority:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""
        files = [os.path.join("models", "neurons", "iaf_psc_delta_neuron.nestml"),
                 os.path.join("tests", "resources", "synapse_event_priority_test.nestml"),
                 os.path.join("tests", "resources", "synapse_event_inv_priority_test.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="INFO",
                             module_name="nestml_module",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                                     "synapse": "event_priority_test_synapse",
                                                                     "post_ports": ["post_spikes"]},
                                                                    {"neuron": "iaf_psc_delta_neuron",
                                                                     "synapse": "event_inv_priority_test_synapse",
                                                                     "post_ports": ["post_spikes"]}]})

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_synapse_event_priority(self):

        fname_snip = ""

        # one additional pre spike to ensure processing of post spikes in the intermediate interval
        pre_spike_times = np.array([3., 50.])
        post_spike_times = np.array([2.])

        self.run_synapse_test(
            resolution=.5,  # [ms]
            delay=1.,  # [ms]
            pre_spike_times=pre_spike_times,
            post_spike_times=post_spike_times,
            fname_snip=fname_snip)

    def run_nest_simulation(self, neuron_model_name,
                            synapse_model_name,
                            resolution=1.,  # [ms]
                            delay=1.,  # [ms]
                            sim_time=None,  # if None, computed from pre and post spike times
                            pre_spike_times=None,
                            post_spike_times=None,
                            fname_snip=""):

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        if sim_time is None:
            sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.set_verbosity("M_ALL")
        # nest.set_verbosity("M_WARNING")
        nest.ResetKernel()
        try:
            nest.Install("nestml_module")
        except Exception:
            pass
        nest.SetKernelStatus({'resolution': resolution})

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        # wr = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name, "syn_nestml",
                       {"d": delay})
        #    {"weight_recorder": wr[0], "d": delay})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        # mm = nest.Create("multimeter", params={"record_from" : ["V_m", "post_trace_kernel__for_stdp_nestml__X__post_spikes__for_stdp_nestml"]})

        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={'synapse_model': 'syn_nestml'})
        # nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        # get STDP synapse
        syn = nest.GetConnections(source=pre_neuron, synapse_model="syn_nestml")

        nest.Simulate(sim_time)

        return syn.get("tr")

    def run_synapse_test(self,
                         resolution=1.,  # [ms]
                         delay=1.,  # [ms]
                         sim_time=None,  # if None, computed from pre and post spike times
                         pre_spike_times=None,
                         post_spike_times=None,
                         fname_snip=""):

        neuron_model_name = "iaf_psc_delta_neuron_nestml__with_event_priority_test_synapse_nestml"
        synapse_model_name = "event_priority_test_synapse_nestml__with_iaf_psc_delta_neuron_nestml"
        tr = self.run_nest_simulation(neuron_model_name=neuron_model_name,
                                      synapse_model_name=synapse_model_name,
                                      resolution=resolution,
                                      delay=delay,
                                      sim_time=sim_time,
                                      pre_spike_times=pre_spike_times,
                                      post_spike_times=post_spike_times,
                                      fname_snip=fname_snip)

        neuron_model_name = "iaf_psc_delta_neuron_nestml__with_event_inv_priority_test_synapse_nestml"
        synapse_model_name = "event_inv_priority_test_synapse_nestml__with_iaf_psc_delta_neuron_nestml"
        tr_inv = self.run_nest_simulation(neuron_model_name=neuron_model_name,
                                          synapse_model_name=synapse_model_name,
                                          resolution=resolution,
                                          delay=delay,
                                          sim_time=sim_time,
                                          pre_spike_times=pre_spike_times,
                                          post_spike_times=post_spike_times,
                                          fname_snip=fname_snip)

        np.testing.assert_allclose(tr, 7.28318)
        np.testing.assert_allclose(tr_inv, 5.14159)
