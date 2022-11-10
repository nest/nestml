# -*- coding: utf-8 -*-
#
# traub_cond_multisyn_test.py
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
import unittest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


class NestWBCondExpTest(unittest.TestCase):

    def test_traub_cond_multisyn(self):

        if not os.path.exists("target"):
            os.makedirs("target")

        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, "models", "neurons", "traub_cond_multisyn.nestml")))
        target_path = "target"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level="INFO",
                             suffix=suffix,
                             module_name=module_name)

        nest.Install("nestmlmodule")
        model = "traub_cond_multisyn_nestml"

        dt = 0.01
        t_simulation = 1000.0
        nest.SetKernelStatus({"resolution": dt})

        neuron1 = nest.Create(model, 1)
        nest.SetStatus(neuron1, {"I_e": 100.0})

        neuron2 = nest.Create(model)
        nest.SetStatus(neuron2, {"tau_AMPA_1": 0.1,
                                 "tau_AMPA_2": 2.4,
                                 "AMPA_g_peak": 0.1})

        multimeter = nest.Create("multimeter", 2)
        if NESTTools.detect_nest_version().startswith("v2"):
            nest.SetStatus([multimeter[0]], {"record_from": ["V_m"],
                                             "interval": dt})
        else:
            nest.SetStatus(multimeter[0], {"record_from": ["V_m"],
                                           "interval": dt})
        record_from = ["V_m", "I_syn_ampa",
                       "I_syn_nmda", "I_syn_gaba_a", "I_syn_gaba_b"]
        if NESTTools.detect_nest_version().startswith("v2"):
            nest.SetStatus([multimeter[1]], {"record_from": record_from,
                                             "interval": dt})
        else:
            nest.SetStatus(multimeter[1], {"record_from": record_from,
                                           "interval": dt})
        # {"AMPA": 1, "NMDA": 2, "GABA_A": 3, "GABA_B": 4}
        nest.Connect(neuron1, neuron2, syn_spec={"receptor_type": 1})  # AMPA
        nest.Connect(neuron1, neuron2, syn_spec={"receptor_type": 2})  # NMDA
        nest.Connect(neuron1, neuron2, syn_spec={"receptor_type": 3})  # GABAA
        nest.Connect(neuron1, neuron2, syn_spec={"receptor_type": 4})  # GABAB

        if NESTTools.detect_nest_version().startswith("v2"):
            nest.Connect([multimeter[0]], neuron1, "one_to_one")
            nest.Connect([multimeter[1]], neuron2)
            spike_recorder = nest.Create("spike_detector")
        else:
            nest.Connect(multimeter[0], neuron1, "one_to_one")
            nest.Connect(multimeter[1], neuron2)
            spike_recorder = nest.Create("spike_recorder")
        nest.Connect(neuron1, spike_recorder)
        nest.Simulate(t_simulation)

        dmm = nest.GetStatus(multimeter)[1]
        Voltages = dmm["events"]["V_m"]
        tv = dmm["events"]["times"]

        dSD = nest.GetStatus(spike_recorder, keys="events")[0]
        spikes = dSD["senders"]
        ts = dSD["times"]

        firing_rate = len(spikes) / t_simulation * 1000
        print("firing rate is ", firing_rate)
        expected_value = np.abs(firing_rate - 40)
        tolerance_value = 5  # Hz

        self.assertLessEqual(expected_value, tolerance_value)

        if TEST_PLOTS:

            fig, ax = plt.subplots(3, figsize=(8, 6), sharex=True)
            ax[0].plot(tv, Voltages, lw=2, label=str(2))
            labels = ["ampa", "nmda", "gaba_a", "gaba_b"]
            j = 0
            for i in record_from[1:]:
                g = dmm["events"][i]
                ax[1].plot(tv, g, lw=2, label=labels[j])
                j += 1

            ax[2].plot(ts, spikes, "k.")
            ax[2].set_xlabel("Time [ms]")
            ax[2].set_xlim(0, t_simulation)
            ax[2].set_ylabel("Spikes")
            ax[0].set_title("recording from PSP")
            ax[0].set_ylabel("v [ms]")
            ax[1].set_ylabel("I_syn")
            ax[1].legend(frameon=False, loc="upper right")

            plt.savefig("traub_cond_multisyn.png")


if __name__ == "__main__":
    unittest.main()
