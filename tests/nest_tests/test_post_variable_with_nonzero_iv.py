# -*- coding: utf-8 -*-
#
# test_post_variable_with_nonzero_iv.py
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

from typing import Sequence

import numpy as np
import os
import pytest

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestPostVariableWithNonzeroIV:

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml"
    synapse_model_name = "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_model_code(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapses": {"stdp_synapse": {"post_ports": ["post_spikes"]}}}],
                        "weight_variable": {"stdp_synapse": "w"}}

        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("tests", "nest_tests", "resources", "test_post_variable_with_nonzero_iv_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="test_stdp_synapse_target_structuralplasticitynode",
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @pytest.mark.parametrize("delay", [1.])
    @pytest.mark.parametrize("resolution", [1.])
    @pytest.mark.parametrize("pre_spike_times,post_spike_times", [
        ([1., 11., 21.],
         [6., 16., 26.])
    ])
    def test_nest_stdp_synapse(self, pre_spike_times: Sequence[float], post_spike_times: Sequence[float], resolution: float, delay: float, fname_snip: str = ""):
        self.run_synapse_test(neuron_model_name=self.neuron_model_name,
                              synapse_model_name=self.synapse_model_name,
                              resolution=resolution,  # [ms]
                              delay=delay,  # [ms]
                              pre_spike_times=pre_spike_times,
                              post_spike_times=post_spike_times,
                              fname_snip=fname_snip)

    def run_synapse_test(self, neuron_model_name,
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

        NESTTools.set_nest_verbosity("ALL")
        nest.ResetKernel()

        # load the generated modules into NEST
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        NESTTools.set_nest_verbosity("ERROR")

        nest.SetKernelStatus({"resolution": resolution})

        wr = nest.Create("weight_recorder")
        nest.CopyModel(synapse_model_name, "stdp_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "delay": 1., "receptor_type": 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times,
                                     "allow_offgrid_times": True})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        # create parrot neurons and connect spike_generators
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(neuron_model_name)

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        mm = nest.Create("multimeter", params={"record_from": [
                         "V_m", "post_trace__for_stdp_synapse_nestml"]})
        nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
        nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 99999.})
        nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "stdp_nestml_rec"})
        nest.Connect(mm, post_neuron)
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)
        syn = nest.GetConnections(source=pre_neuron, synapse_model="stdp_nestml_rec")

        n_steps = int(np.ceil(sim_time / resolution)) + 1
        t = 0.
        t_hist = []
        w_hist = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            w_hist.append(nest.GetStatus(syn)[0]["w"])

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["post_trace__for_stdp_synapse_nestml"], label="post_tr nestml")
            ax1.plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax1, ax2, ax3 = ax

            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            print("Actual pre spike times: " + str(pre_spike_times_))
            n_spikes = len(pre_spike_times_)
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
            print("Actual post spike times: " + str(post_spike_times_))
            ax1.set_ylabel("Pre spikes")

            n_spikes = len(post_spike_times_)
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nestml"
                else:
                    _lbl = None
                ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)

            ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["post_trace__for_stdp_synapse_nestml"], label="nestml post tr")
            ax2.set_ylabel("Post spikes")

            ax3.plot(t_hist, w_hist, marker="o", label="nestml")

            ax3.set_xlabel("Time [ms]")
            ax3.set_ylabel("w")
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/stdp_synapse_test" + fname_snip + ".png", dpi=300)

        # verify
        assert False
