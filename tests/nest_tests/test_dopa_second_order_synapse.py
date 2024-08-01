# -*- coding: utf-8 -*-
#
# test_dopa_second_order_synapse.py
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


class TestDopaSecondOrder:
    r"""
    Test second-order integration in a neuromodulated synapse.
    """

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_dopa_second_order_synapse_nestml"
    synapse_model_name = "dopa_second_order_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""generate code for neuron and synapse and build NEST user module"""
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "dopa_second_order_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "dopa_second_order_synapse",
                                                                     "vt_ports": ["dopa_spikes"]}],
                                           "delay_variable": {"dopa_second_order_synapse": "d"},
                                           "weight_variable": {"dopa_second_order_synapse": "w"}})

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_synapse(self):

        resolution = .25   # [ms]
        delay = 1.    # [ms]
        t_stop = 250.    # [ms]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
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

        # set up custom synapse model
        wr = nest.Create("weight_recorder")
        nest.CopyModel(self.synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "d": delay, "receptor_type": 0,
                        "volume_transmitter": vt})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(self.neuron_model_name)
        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": "stdp_nestml_rec"})

        syn = nest.GetConnections(pre_neuron, post_neuron)
        syn.tau_dopa = 25.   # [ms]

        # run the NEST simulation
        log = {"t": [0.],
               "dopa_rate": [syn.dopa_rate],
               "dopa_rate_d": [syn.dopa_rate_d]}

        n_timesteps = int(np.ceil(t_stop / resolution))
        for timestep in range(n_timesteps):
            nest.Simulate(resolution)
            log["t"].append(nest.biological_time)
            log["dopa_rate"].append(syn.dopa_rate)
            log["dopa_rate_d"].append(syn.dopa_rate_d)

        # run the reference simulation
        ref_log = {"t": np.arange(0., nest.biological_time + 1E-12, resolution),
                   "dopa_rate": [0.],
                   "dopa_rate_d": [0.]}

        for t in ref_log["t"][1:]:
            d_dopa_rate = resolution * ref_log["dopa_rate_d"][-1]
            d_d_dopa_rate = resolution * (-ref_log["dopa_rate"][-1] / syn.tau_dopa**2 - 2 * ref_log["dopa_rate_d"][-1] / syn.tau_dopa)
            ref_log["dopa_rate"].append(ref_log["dopa_rate"][-1] + d_dopa_rate)
            ref_log["dopa_rate_d"].append(ref_log["dopa_rate_d"][-1] + d_d_dopa_rate)

            for t_sp in np.array(sr.get("events")["times"]) + 1:
                if np.abs(t - t_sp) < 1E-12:
                    ref_log["dopa_rate_d"][-1] += 1 / syn.tau_dopa

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2, dpi=300)
            ax[0].plot(log["t"], log["dopa_rate"], label="dopa_rate (NEST)")
            ax[1].plot(log["t"], log["dopa_rate_d"], label="dopa_rate_d (NEST)")
            ax[0].plot(ref_log["t"], ref_log["dopa_rate"], label="dopa_rate (ref)")
            ax[1].plot(ref_log["t"], ref_log["dopa_rate_d"], label="dopa_rate_d (ref)")
            for _ax in ax:
                _ax.legend()
            fig.savefig("/tmp/test_dopa_second_order_synapse.png")
            plt.close(fig)

        np.testing.assert_allclose(log["dopa_rate"][-1], 0.6834882070000989)
