# -*- coding: utf-8 -*-
#
# test_continuous_third_factor_in_modulatory_spikes_handler.py
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
import pytest
import re

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestContinuousThirdFactorInModulatorySpikesHandler:
    r"""Test that continuous third factors can be accessed in the modulatory spikes handler in a synapse model."""

    @pytest.fixture(scope="module", autouse=True)
    def generate_all_models(self):
        codegen_opts = {"continuous_state_buffering_method": "post_spike_based",
                        "neuron_synapse_pairs": [{"neuron": "test_continuous_third_factor_in_modulatory_spikes_handler_neuron",
                                                  "synapse": "test_continuous_third_factor_in_modulatory_spikes_handler_synapse",
                                                  "vt_ports": ["mod_spikes"],
                                                  "post_ports": ["post_spikes",
                                                                 ["e_trace_d", "e_trace_dend"]]}],
                        "delay_variable": {"test_continuous_third_factor_in_modulatory_spikes_handler_synapse": "d"},
                        "weight_variable": {"test_continuous_third_factor_in_modulatory_spikes_handler_synapse": "w"}}

        generate_nest_target(input_path=["tests/nest_tests/resources/test_continuous_third_factor_in_modulatory_spikes_handler_neuron.nestml",
                                         "tests/nest_tests/resources/test_continuous_third_factor_in_modulatory_spikes_handler_synapse.nestml"],
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    def test_continuous_third_factor_in_modulatory_spikes_handler(self):
        t_stop = 100.    # [ms]

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        # create spike_generator
        vt_sg = nest.Create("poisson_generator",
                            params={"rate": 20.})

        # create volume transmitter
        vt = nest.Create("volume_transmitter")
        vt_parrot = nest.Create("parrot_neuron")
        nest.Connect(vt_sg, vt_parrot)
        sr = nest.Create("spike_recorder")
        nest.Connect(vt_parrot, sr)
        nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                              "weight": 1.,
                                              "delay": 1.})   # delay is ignored!

        nestml_model_name = "test_continuous_third_factor_in_modulatory_spikes_handler_neuron_nestml__with_test_continuous_third_factor_in_modulatory_spikes_handler_synapse_nestml"
        synapse_model_name = "test_continuous_third_factor_in_modulatory_spikes_handler_synapse_nestml__with_test_continuous_third_factor_in_modulatory_spikes_handler_neuron_nestml"

        neuron1 = nest.Create("parrot_neuron")
        neuron2 = nest.Create(nestml_model_name)
        nest.CopyModel(synapse_model_name, "my_nestml_synapse", {"volume_transmitter": vt})
        nest.Connect(neuron1, neuron2, syn_spec={"synapse_model": "my_nestml_synapse", "weight": 1., "delay": 1.})

        sg = nest.Create("spike_generator",
                         params={"spike_times": [20., 50., 80.]})
        nest.Connect(sg, neuron1, syn_spec={"synapse_model": "static_synapse", "weight": 1., "delay": 1.})

        multimeter2 = nest.Create("multimeter")

        V_m_specifier = "V_m"  # "delta_V_m"
        nest.SetStatus(multimeter2, {"record_from": [V_m_specifier]})

        nest.Connect(multimeter2, neuron2)

        sd_pre_neuron = nest.Create("spike_recorder")
        sd_post_neuron = nest.Create("spike_recorder")

        nest.Connect(neuron1, sd_pre_neuron)
        nest.Connect(neuron2, sd_post_neuron)

        nest.Simulate(t_stop)

        syn = nest.GetConnections(neuron1, neuron2)[0]
        e_trace_d_read = syn.e_trace_d_read
        e_trace_d_mod = syn.e_trace_d_mod
        np.testing.assert_allclose(e_trace_d_read, 42)
        np.testing.assert_allclose(e_trace_d_mod, 42)
