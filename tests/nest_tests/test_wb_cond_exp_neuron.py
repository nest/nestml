# -*- coding: utf-8 -*-
#
# test_wb_cond_exp_neuron.py
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


class TestWBCondExpNeuron:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""
        files = [os.path.join("models", "neurons", "wb_cond_exp_neuron.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml")

    def run_nest_simulation(self, spike_times_exc, spike_times_inh):
        sim_time = max(np.amax(spike_times_exc), np.amax(spike_times_inh)) + 100.

        nest.ResetKernel()
        nest.resolution = .01
        NESTTools.set_nest_verbosity("ALL")
        try:
            nest.Install("nestmlmodule")
        except Exception:
            pass

        sg_exc = nest.Create("spike_generator",
                             params={"spike_times": spike_times_exc})
        sg_inh = nest.Create("spike_generator",
                             params={"spike_times": spike_times_inh})
        mm = nest.Create("multimeter", params={"record_from": ["V_m", "I_syn_exc", "I_syn_inh"],
                                               "interval": nest.resolution})
        neuron = nest.Create("wb_cond_exp_neuron_nestml")
        sr = nest.Create("spike_recorder")

        nest.Connect(mm, neuron)
        nest.Connect(sg_exc, neuron, syn_spec={"weight": 100})
        nest.Connect(sg_inh, neuron, syn_spec={"weight": -100})
        nest.Connect(neuron, sr)

        nest.Simulate(sim_time)

        return mm.events["times"], mm.events["I_syn_exc"], mm.events["I_syn_inh"], mm.events["V_m"]

    def test_wb_cond_exp_neuron_currents(self):
        spike_times_exc = np.array([1.])
        spike_times_inh = np.array([100.])

        timevec, I_syn_exc, I_syn_inh, V_m = self.run_nest_simulation(spike_times_exc, spike_times_inh)

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)
            ax[0].plot(timevec, I_syn_exc)
            ax[0].set_ylabel("I_syn_exc")
            ax[1].plot(timevec, I_syn_inh)
            ax[1].set_ylabel("I_syn_inh")
            ax[2].plot(timevec, V_m)
            ax[2].set_ylabel("V_m")
            ax[-1].set_xlabel("Time [ms]")
            fig.savefig("/tmp/test_wb_cond_exp_neuron.png")

        # check that I_syn_exc is positive
        assert np.amax(I_syn_exc) > 0
        # assert np.amin(I_syn_exc) == 0    # can't enforce this! note that I_syn_exc is prone to reversing sign when the membrane potential makes large swings (like during an action potential)

        # check that I_syn_inh is negative
        assert np.amin(I_syn_inh) < 0
        assert np.amax(I_syn_inh) == 0

    def test_wb_cond_exp_neuron_firing(self):
        nest.ResetKernel()
        nest.resolution = .01
        NESTTools.set_nest_verbosity("ALL")
        try:
            nest.Install("nestmlmodule")
        except Exception:
            pass

        t_simulation = 1000.0

        neuron = nest.Create("wb_cond_exp_neuron_nestml")
        nest.SetStatus(neuron, {"I_e": 75.0})
        multimeter = nest.Create("multimeter")
        nest.SetStatus(multimeter, {"record_from": ["V_m"],
                                    "interval": nest.resolution})
        spike_recorder = nest.Create("spike_recorder")
        nest.Connect(multimeter, neuron)
        nest.Connect(neuron, spike_recorder)
        nest.Simulate(t_simulation)

        dmm = nest.GetStatus(multimeter)[0]
        Voltages = dmm["events"]["V_m"]
        tv = dmm["events"]["times"]
        dSD = nest.GetStatus(spike_recorder, keys="events")[0]
        spikes = dSD["senders"]
        ts = dSD["times"]

        firing_rate = len(spikes) / t_simulation * 1000
        print("firing rate is ", firing_rate)

        if TEST_PLOTS:
            fig, ax = plt.subplots(2, figsize=(8, 6), sharex=True)
            ax[0].plot(tv, Voltages, lw=2, color="k")
            ax[1].plot(ts, spikes, "ko")
            ax[1].set_xlabel("Time [ms]")
            ax[1].set_xlim(0, t_simulation)
            ax[1].set_ylabel("Spikes")
            ax[0].set_ylabel("v [ms]")
            ax[0].set_ylim(-100, 50)

            for i in ts:
                ax[0].axvline(x=i, lw=1., ls="--", color="gray")

            plt.savefig("/tmp/wb_cond_exp.png")

        expected_firing_rate = 50    # [Hz]
        tolerance_value = 5    # [Hz]
        assert abs(firing_rate - expected_firing_rate) <= tolerance_value
