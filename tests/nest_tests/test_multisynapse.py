# -*- coding: utf-8 -*-
#
# test_multisynapse.py
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

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNestMultiSynapse:

    def test_multisynapse(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "iaf_psc_exp_multisynapse.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             suffix=suffix)

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.resolution = 0.1
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        # network construction
        neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

        receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

        sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
        nest.Connect(sg, neuron, syn_spec={"receptor_type": receptor_types["SPIKES1"], "weight": 1000., "delay": 0.1})

        sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
        nest.Connect(sg2, neuron, syn_spec={"receptor_type": receptor_types["SPIKES2"], "weight": 1000., "delay": 0.1})

        sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
        nest.Connect(sg3, neuron, syn_spec={"receptor_type": receptor_types["SPIKES3"], "weight": 500., "delay": 0.1})

        mm = nest.Create("multimeter", params={"record_from": [
                         "I_syn", "I_kernel2__X__spikes2", "I_kernel3__X__spikes3"], "interval": nest.resolution})
        nest.Connect(mm, neuron)

        vm_1 = nest.Create("voltmeter", params={"interval": nest.resolution})
        nest.Connect(vm_1, neuron)

        # simulate
        nest.Simulate(125.)

        # analysis
        V_m_timevec = nest.GetStatus(vm_1)[0]["events"]["times"]
        V_m = nest.GetStatus(vm_1)[0]["events"]["V_m"]
        mm = nest.GetStatus(mm)[0]["events"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)

            ax[0].plot(V_m_timevec, V_m, label="V_m")
            ax[0].set_ylabel("voltage")

            ax[1].plot(mm["times"], mm["I_syn"], label="I_syn")
            ax[1].set_ylabel("current")

            ax[2].plot(mm["times"], mm["I_kernel2__X__spikes2"], label="I_kernel2")
            ax[2].set_ylabel("current")

            ax[3].plot(mm["times"], mm["I_kernel3__X__spikes3"], label="I_kernel3")
            ax[3].set_ylabel("current")

            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.set_xlim(0., 125.)
                _ax.grid(True)

            for _ax in ax[:-1]:
                _ax.set_xticklabels([])

            ax[-1].set_xlabel("time")

            fig.savefig("/tmp/test_multisynapse.png")

        # testing
        np.testing.assert_almost_equal(V_m[-1], -72.58743039242219)

    def test_multisynapse_with_vector_input_ports(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "iaf_psc_exp_multisynapse_vectors.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             suffix=suffix)

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.resolution = 0.1
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        # network construction
        neuron = nest.Create("iaf_psc_exp_multisynapse_vectors_neuron_nestml")

        # List of receptor types for the spiking input ports
        receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

        sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
        nest.Connect(sg, neuron, syn_spec={"receptor_type": receptor_types["SPIKES_VEC_IDX_0"], "weight": 1000., "delay": 0.1})

        sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
        nest.Connect(sg2, neuron, syn_spec={"receptor_type": receptor_types["SPIKES_VEC_IDX_1"], "weight": 1000., "delay": 0.1})

        sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
        nest.Connect(sg3, neuron, syn_spec={"receptor_type": receptor_types["SPIKES_VEC_IDX_2"], "weight": 500., "delay": 0.1})

        mm = nest.Create("multimeter", params={"record_from": [
            "I_kernel1__X__spikes_0", "I_kernel2__X__spikes_1", "I_kernel3__X__spikes_2"], "interval": nest.resolution})
        nest.Connect(mm, neuron)

        vm_1 = nest.Create("voltmeter", params={"interval": nest.resolution})
        nest.Connect(vm_1, neuron)

        # simulate
        nest.Simulate(125.)

        # analysis
        V_m_timevec = nest.GetStatus(vm_1)[0]["events"]["times"]
        V_m = nest.GetStatus(vm_1)[0]["events"]["V_m"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=4)

            ax[0].plot(V_m_timevec, V_m, label="V_m")
            ax[0].set_ylabel("voltage")

            ax[1].plot(mm.events["times"], mm.events["I_kernel1__X__spikes_0"], label="I_kernel0")
            ax[1].set_ylabel("current")

            ax[2].plot(mm.events["times"], mm.events["I_kernel2__X__spikes_1"], label="I_kernel1")
            ax[2].set_ylabel("current")

            ax[3].plot(mm.events["times"], mm.events["I_kernel3__X__spikes_2"], label="I_kernel2")
            ax[3].set_ylabel("current")

            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.set_xlim(0., 125.)
                _ax.grid(True)

            for _ax in ax[:-1]:
                _ax.set_xticklabels([])

            ax[-1].set_xlabel("time")

            fig.savefig("/tmp/test_multisynapse_vector.png")

        # testing
        np.testing.assert_almost_equal(V_m[-1], -72.77067117288824)
