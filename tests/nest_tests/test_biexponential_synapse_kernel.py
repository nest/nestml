# -*- coding: utf-8 -*-
#
# test_biexponential_synapse_kernel.py
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

import nest
import numpy as np
import os
import pytest

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
class TestNestBiexponentialSynapse:

    def test_biexp_synapse(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(
            __file__), "resources", "BiexponentialPostSynapticResponse.nestml")))
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install(module_name)

        # network construction

        neuron = nest.Create("biexp_postsynaptic_response_neuron_nestml", params={"V_th": 999.})

        sd = nest.Create("spike_recorder")
        nest.Connect(neuron, sd)

        sg = nest.Create("spike_generator", params={"spike_times": [10., 30.]})
        nest.Connect(sg, neuron, syn_spec={"receptor_type": 1, "weight": 100.})

        sg2 = nest.Create("spike_generator", params={"spike_times": [20., 40.]})
        nest.Connect(sg2, neuron, syn_spec={"receptor_type": 2, "weight": 100.})

        sg3 = nest.Create("spike_generator", params={"spike_times": [25., 45.]})
        nest.Connect(sg3, neuron, syn_spec={"receptor_type": 3, "weight": 100.})

        sg4 = nest.Create("spike_generator", params={"spike_times": [35., 55.]})
        nest.Connect(sg4, neuron, syn_spec={"receptor_type": 4, "weight": 100.})

        i_1 = nest.Create("multimeter", params={"record_from": [
                          "g_gap__X__spikeGap", "g_ex__X__spikeExc", "g_in__X__spikeInh", "g_GABA__X__spikeGABA"], "interval": .1})
        nest.Connect(i_1, neuron)

        vm_1 = nest.Create("voltmeter")
        nest.Connect(vm_1, neuron)

        # simulate

        nest.Simulate(80.)

        # analysis

        vm_1 = nest.GetStatus(vm_1)[0]["events"]
        i_1 = nest.GetStatus(i_1)[0]["events"]
        if TEST_PLOTS:
            self.plot(vm_1, i_1, sd)

        # verification
        final_v_m = vm_1["V_m"][-1]
        print("final V_m = " + str(final_v_m))
        np.testing.assert_allclose(final_v_m, -61.881497)

    def plot(self, vm_1, i_1, sd):
        fig, ax = plt.subplots(nrows=5)

        ax[0].plot(vm_1["times"], vm_1["V_m"], label="V_m")
        ax[0].set_ylabel("voltage")

        ax[0].scatter(sd.events["times"], np.mean(vm_1["V_m"]) * np.ones_like(sd.events["times"]))

        ax[1].plot(i_1["times"], i_1["g_gap__X__spikeGap"], label="g_gap__X__spikeGap")
        ax[1].set_ylabel("current")

        ax[2].plot(i_1["times"], i_1["g_ex__X__spikeExc"], label="g_ex__X__spikeExc")
        ax[2].set_ylabel("current")

        ax[3].plot(i_1["times"], i_1["g_in__X__spikeInh"], label="g_in__X__spikeInh")
        ax[3].set_ylabel("current")

        ax[4].plot(i_1["times"], i_1["g_GABA__X__spikeGABA"], label="g_GABA__X__spikeGABA")
        ax[4].set_ylabel("current")

        for _ax in ax:
            # _ax.legend()
            _ax.legend(loc="upper right")
            _ax.set_xlim(0., 80.)
            _ax.grid(True)

        for _ax in ax[:-1]:
            _ax.set_xticklabels([])

        ax[-1].set_xlabel("time")

        fig.savefig("/tmp/biexp_synapse_test.png")
