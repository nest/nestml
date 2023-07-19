# -*- coding: utf-8 -*-
#
# test_clopath_synapse.py
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


class TestClopathSynapse:

    neuron_model_name = "aeif_psc_delta_nestml__with_clopath_synapse_nestml"
    synapse_model_name = "clopath_synapse_nestml__with_aeif_psc_delta_nestml"

    ref_neuron_model_name = "aeif_psc_delta_clopath"
    ref_synapse_model_name = "clopath_synapse"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "aeif_psc_delta",
                                                      "synapse": "clopath_synapse",
                                                      "post_ports": ["post_spikes",
                                                                     ["post_membrane_potential", "V_m"]]}]}

        files = [os.path.join("models", "neurons", "aeif_psc_delta.nestml"),
                 os.path.join("models", "synapses", "clopath_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        # generate_nest_target(input_path=input_path,
        #                      logging_level="DEBUG",
        #                      suffix="_nestml",
        #                      codegen_opts=codegen_opts)

        nest.Install("nestmlmodule")

    def test_nest_clopath_synapse(self):
        fname_snip = ""

        pre_spike_times = [1., 11., 21.]    # [ms]
        post_spike_times = [6., 16., 26.]  # [ms]

        delay = 1.   # [ms]

        if pre_spike_times is None:
            pre_spike_times = []

        if post_spike_times is None:
            post_spike_times = []

        resolution = .1    # [ms]
        sim_time = max(np.amax(pre_spike_times), np.amax(post_spike_times)) + 5 * delay

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()

        print("Pre spike times: " + str(pre_spike_times))
        print("Post spike times: " + str(post_spike_times))

        # nest.set_verbosity("M_WARNING")
        nest.set_verbosity("M_ERROR")

        post_weights = {"parrot": []}

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        wr = nest.Create("weight_recorder")
        wr_ref = nest.Create("weight_recorder")
        nest.CopyModel(self.synapse_model_name, "clopath_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": 1., "receptor_type": 0})
        nest.CopyModel(self.ref_synapse_model_name, "clopath_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": 1., "receptor_type": 0})

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        post_sg = nest.Create("spike_generator",
                              params={"spike_times": post_spike_times,
                                      "allow_offgrid_times": True})

        # create parrot neurons and connect spike_generators
        if sim_mdl:
            pre_neuron = nest.Create("parrot_neuron")
            post_neuron = nest.Create(self.neuron_model_name)

        if sim_ref:
            pre_neuron_ref = nest.Create("parrot_neuron")
            post_neuron_ref = nest.Create(self.ref_neuron_model_name)

        if sim_mdl:
            spikedet_pre = nest.Create("spike_recorder")
            spikedet_post = nest.Create("spike_recorder")
            mm = nest.Create("multimeter", params={"record_from": [
                             "V_m", "post_membrane_potential_avg_plus__for_clopath_synapse_nestml", "post_membrane_potential_avg_minus__for_clopath_synapse_nestml", "post_membrane_avg_avg__for_clopath_synapse_nestml"]})
        if sim_ref:
            spikedet_pre_ref = nest.Create("spike_recorder")
            spikedet_post_ref = nest.Create("spike_recorder")
            mm_ref = nest.Create("multimeter", params={"record_from": ["V_m"]})

        if sim_mdl:
            nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
            nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "clopath_nestml_rec"})
            nest.Connect(mm, post_neuron)
            nest.Connect(pre_neuron, spikedet_pre)
            nest.Connect(post_neuron, spikedet_post)
        if sim_ref:
            nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
            nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_neuron_ref, post_neuron_ref, "all_to_all",
                            syn_spec={"synapse_model": self.ref_synapse_model_name})
            nest.Connect(mm_ref, post_neuron_ref)
            nest.Connect(pre_neuron_ref, spikedet_pre_ref)
            nest.Connect(post_neuron_ref, spikedet_post_ref)

        # get Clopath synapse and weight before protocol
        if sim_mdl:
            syn = nest.GetConnections(source=pre_neuron, synapse_model="clopath_nestml_rec")
        if sim_ref:
            syn_ref = nest.GetConnections(source=pre_neuron_ref, synapse_model=self.ref_synapse_model_name)

        n_steps = int(np.ceil(sim_time / resolution)) + 1
        t = 0.
        t_hist = []
        if sim_mdl:
            w_hist = []
        if sim_ref:
            w_hist_ref = []
        while t <= sim_time:
            nest.Simulate(resolution)
            t += resolution
            t_hist.append(t)
            if sim_ref:
                w_hist_ref.append(nest.GetStatus(syn_ref)[0]["weight"])
            if sim_mdl:
                w_hist.append(nest.GetStatus(syn)[0]["w"])

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)

            if sim_mdl:
                timevec = nest.GetStatus(mm, "events")[0]["times"]
                V_m = nest.GetStatus(mm, "events")[0]["V_m"]
                ax[0].plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")
                ax[1].plot(timevec, nest.GetStatus(mm, "events")[0]["post_membrane_potential_avg_plus__for_clopath_synapse_nestml"], label="V_m avg+")
                ax[2].plot(timevec, nest.GetStatus(mm, "events")[0]["post_membrane_potential_avg_minus__for_clopath_synapse_nestml"], label="V_m avg-")
                ax[3].plot(timevec, nest.GetStatus(mm, "events")[0]["post_membrane_avg_avg__for_clopath_synapse_nestml"], label="V_m avg avg")
            if sim_ref:
                pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
                timevec = nest.GetStatus(mm_ref, "events")[0]["times"]
                V_m = nest.GetStatus(mm_ref, "events")[0]["V_m"]
                ax[0].plot(timevec, V_m, label="nest ref", alpha=.7)
            ax[0].set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/clopath_synapse_test_" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax1, ax2, ax3 = ax

            if sim_mdl:
                pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
                print("Actual pre spike times: " + str(pre_spike_times_))
            if sim_ref:
                pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
                print("Actual pre ref spike times: " + str(pre_ref_spike_times_))

            if sim_mdl:
                n_spikes = len(pre_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            if sim_mdl:
                post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
                print("Actual post spike times: " + str(post_spike_times_))
            if sim_ref:
                post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
                print("Actual post ref spike times: " + str(post_ref_spike_times_))

            if sim_ref:
                n_spikes = len(pre_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1],
                             linewidth=2, color="cyan", label=_lbl, alpha=.4)
            ax1.set_ylabel("Pre spikes")

            if sim_mdl:
                n_spikes = len(post_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            if sim_ref:
                n_spikes = len(post_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_ref_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4, label=_lbl)
            ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["post_membrane_potential_avg_plus__for_clopath_synapse_nestml"], label="nestml post tr")
            ax2.set_ylabel("Post spikes")

            if sim_mdl:
                ax3.plot(t_hist, w_hist, marker="o", label="nestml")
            if sim_ref:
                ax3.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")

            ax3.set_xlabel("Time [ms]")
            ax3.set_ylabel("w")
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/clopath_synapse_test" + fname_snip + ".png", dpi=300)

        # verify





    def test_nest_clopath_synapse_spike_frequency(self):
        fname_snip = ""

        # generate spike times
        n_repeats: int = 1
        n_pairs: int = 5
        delay_between_repeats: float = 4.    # [s]
        delay_between_pre_post_pair: float = 2E-3    # [s]
        pair_frequency = np.linspace(1., 50., 3)
        delay_between_pairs = 1 / pair_frequency

        dw = np.zeros_like(delay_between_pairs)
        for d_idx, d in enumerate(delay_between_pairs):
            t = 100E-3   # initial pair offset [s]
            pre_spike_times = []
            post_spike_times = []
            for repeat_idx in range(n_repeats):
                for pair_idx in range(n_pairs):
                    pre_spike_times.append(t)
                    t += delay_between_pre_post_pair
                    post_spike_times.append(t)
                    t += d

                t += delay_between_repeats

            dw[d_idx] = self._run_experiment(d, pre_spike_times, post_spike_times)

        fig, ax = plt.subplots()
        ax.plot(pair_frequency, dw)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Change in weight [%]")
        fig.savefig("/tmp/clopath_frequency_dependence.png")


    def _run_experiment(self, d, pre_spike_times, post_spike_times):

        fname_snip = "_[f="+str(1/d) + "]"

        delay = 1.   # [ms]

        resolution = .1    # [ms]
        sim_time = 1E3 * np.ceil(max(np.amax(pre_spike_times), np.amax(post_spike_times))) + 5 * delay

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        nest.set_verbosity("M_ALL")

        wr = nest.Create("weight_recorder")
        wr_ref = nest.Create("weight_recorder")
        nest.CopyModel(self.synapse_model_name, "clopath_nestml_rec",
                       {"weight_recorder": wr[0], "w": 1., "d": 1., "receptor_type": 0})
        nest.CopyModel(self.ref_synapse_model_name, "clopath_ref_rec",
                       {"weight_recorder": wr_ref[0], "weight": 1., "delay": 1., "receptor_type": 0})

        # # create spike_generators with these times
        # pre_sg = nest.Create("spike_generator",
        #                      params={"spike_times": pre_spike_times})
        # post_sg = nest.Create("spike_generator",
        #                       params={"spike_times": post_spike_times,
        #                               "allow_offgrid_times": True})

        # create parrot neurons and connect spike_generators
        if sim_mdl:
            pre_neuron = nest.Create(self.neuron_model_name)
            post_neuron = nest.Create(self.neuron_model_name)
            pre_cg_time_values = []
            pre_cg_amplitude_values = []
            for t in pre_spike_times:
                pre_cg_time_values.append(1E3 * t - nest.resolution)
                pre_cg_amplitude_values.append(1000000.)
                pre_cg_time_values.append(1E3 * t)
                pre_cg_amplitude_values.append(0.)
            pre_cg_params = {"amplitude_times": pre_cg_time_values, "amplitude_values": pre_cg_amplitude_values, "allow_offgrid_times": True}
            pre_cg = nest.Create("step_current_generator", params=pre_cg_params)

            post_cg_time_values = []
            post_cg_amplitude_values = []
            for t in post_spike_times:
                post_cg_time_values.append(1E3 * t - nest.resolution)
                post_cg_amplitude_values.append(1000000.)
                post_cg_time_values.append(1E3 * t)
                post_cg_amplitude_values.append(0.)
            post_cg_params = {"amplitude_times": post_cg_time_values, "amplitude_values": post_cg_amplitude_values, "allow_offgrid_times": True}
            post_cg = nest.Create("step_current_generator", params=post_cg_params)

        if sim_ref:
            pre_neuron_ref = nest.Create(self.ref_neuron_model_name)
            post_neuron_ref = nest.Create(self.ref_neuron_model_name)

        if sim_mdl:
            spikedet_pre = nest.Create("spike_recorder")
            spikedet_post = nest.Create("spike_recorder")
            mm = nest.Create("multimeter", params={"record_from": [
                             "V_m", "post_membrane_potential_avg_plus__for_clopath_synapse_nestml", "post_membrane_potential_avg_minus__for_clopath_synapse_nestml", "post_membrane_avg_avg__for_clopath_synapse_nestml"]})
        if sim_ref:
            spikedet_pre_ref = nest.Create("spike_recorder")
            spikedet_post_ref = nest.Create("spike_recorder")
            mm_ref = nest.Create("multimeter", params={"record_from": ["V_m"]})

        if sim_mdl:
            # nest.Connect(pre_sg, pre_neuron, "one_to_one", syn_spec={"delay": 1.})
            # nest.Connect(post_sg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_cg, pre_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 1.})
            nest.Connect(post_cg, post_neuron, "one_to_one", syn_spec={"delay": 1., "weight": 1.})

            nest.Connect(pre_neuron, post_neuron, "all_to_all", syn_spec={"synapse_model": "clopath_nestml_rec"})

            nest.Connect(mm, post_neuron)
            nest.Connect(pre_neuron, spikedet_pre)
            nest.Connect(post_neuron, spikedet_post)
        if sim_ref:
            # nest.Connect(pre_sg, pre_neuron_ref, "one_to_one", syn_spec={"delay": 1.})
            # nest.Connect(post_sg, post_neuron_ref, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
            nest.Connect(pre_neuron_ref, post_neuron_ref, "all_to_all",
                            syn_spec={"synapse_model": self.ref_synapse_model_name})
            nest.Connect(mm_ref, post_neuron_ref)
            nest.Connect(pre_neuron_ref, spikedet_pre_ref)
            nest.Connect(post_neuron_ref, spikedet_post_ref)

        # get Clopath synapse and weight before protocol
        if sim_mdl:
            syn = nest.GetConnections(source=pre_neuron, synapse_model="clopath_nestml_rec")
        if sim_ref:
            syn_ref = nest.GetConnections(source=pre_neuron_ref, synapse_model=self.ref_synapse_model_name)


        nest.Simulate(sim_time)



        if sim_mdl:
            print("Intended (length " + str(len(pre_spike_times)) + ") pre spike times: " + str(pre_spike_times))
            pre_spike_times_ = nest.GetStatus(spikedet_pre, "events")[0]["times"]
            print("Actual (length " + str(len(pre_spike_times_)) + ") pre spike times: " + str(pre_spike_times_))
        if sim_ref:
            pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
            print("Actual pre ref spike times: " + str(pre_ref_spike_times_))

        if sim_mdl:
            post_spike_times_ = nest.GetStatus(spikedet_post, "events")[0]["times"]
            print("Actual post spike times: " + str(post_spike_times_))
        if sim_ref:
            post_ref_spike_times_ = nest.GetStatus(spikedet_post_ref, "events")[0]["times"]
            print("Actual post ref spike times: " + str(post_ref_spike_times_))


        # n_steps = int(np.ceil(sim_time / resolution)) + 1
        # t = 0.
        # t_hist = []
        # if sim_mdl:
        #     w_hist = []
        # if sim_ref:
        #     w_hist_ref = []
        # while t <= sim_time:
        #     nest.Simulate(1000 * resolution)
        #     t += resolution
        #     t_hist.append(t)
        #     if sim_ref:
        #         w_hist_ref.append(nest.GetStatus(syn_ref)[0]["weight"])
        #     if sim_mdl:
        #         w_hist.append(nest.GetStatus(syn)[0]["w"])
        #     print(str(int(np.round(t / sim_time * 100))) + " %")

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3, figsize=(12, 4))

            if sim_mdl:
                n_spikes = len(pre_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax[0].plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)
                n_spikes = len(post_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax[1].plot(2 * [post_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)
            if sim_ref:
                n_spikes = len(pre_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest"
                    else:
                        _lbl = None
                    ax[0].plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)
                n_spikes = len(post_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest"
                    else:
                        _lbl = None
                    ax[1].plot(2 * [post_ref_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)




            ax[2].plot(pre_cg_time_values, pre_cg_amplitude_values)

            ax[0].set_ylabel("Pre spikes")
            ax[1].set_ylabel("Post spikes")

            for _ax in ax:
                _ax.grid()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/clopath_synapse_test" + fname_snip + "_spikes.png", dpi=300)





        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)

            if sim_mdl:
                n_spikes = len(pre_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax[0].plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)
            if sim_ref:
                pre_ref_spike_times_ = nest.GetStatus(spikedet_pre_ref, "events")[0]["times"]
                timevec = nest.GetStatus(mm_ref, "events")[0]["times"]
                V_m = nest.GetStatus(mm_ref, "events")[0]["V_m"]
                ax[0].plot(timevec, V_m, label="nest ref", alpha=.7)
            ax[0].set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/clopath_synapse_test" + fname_snip + "_V_m.png", dpi=300)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax1, ax2, ax3 = ax

            if sim_mdl:
                n_spikes = len(pre_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_spike_times_[i] + delay], [0, 1], linewidth=2, color="blue", alpha=.4, label=_lbl)

            if sim_ref:
                n_spikes = len(pre_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax1.plot(2 * [pre_ref_spike_times_[i] + delay], [0, 1],
                             linewidth=2, color="cyan", label=_lbl, alpha=.4)
            ax1.set_ylabel("Pre spikes")

            if sim_mdl:
                n_spikes = len(post_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nestml"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_spike_times_[i]], [0, 1], linewidth=2, color="black", alpha=.4, label=_lbl)
            if sim_ref:
                n_spikes = len(post_ref_spike_times_)
                for i in range(n_spikes):
                    if i == 0:
                        _lbl = "nest ref"
                    else:
                        _lbl = None
                    ax2.plot(2 * [post_ref_spike_times_[i]], [0, 1], linewidth=2, color="red", alpha=.4, label=_lbl)
            ax2.plot(timevec, nest.GetStatus(mm, "events")[0]["post_membrane_potential_avg_plus__for_clopath_synapse_nestml"], label="nestml post tr")
            ax2.set_ylabel("Post spikes")

            # if sim_mdl:
            #     ax3.plot(t_hist, w_hist, marker="o", label="nestml")
            # if sim_ref:
            #     ax3.plot(t_hist, w_hist_ref, linestyle="--", marker="x", label="ref")

            ax3.set_xlabel("Time [ms]")
            ax3.set_ylabel("w")
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator(np.arange(0, np.ceil(sim_time))))
                _ax.set_xlim(0., sim_time)
                _ax.legend()
            fig.savefig("/tmp/clopath_synapse_test" + fname_snip + ".png", dpi=300)

        return syn.w





