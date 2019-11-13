#
# nest_multisynapse_test.py
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
import os
import numpy as np
import unittest
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except:
    TEST_PLOTS = False


class NESTMultiSynapseTest(unittest.TestCase):
    def test(self):
        #
        #   generate and build multisynapse NESTML test model
        #

        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")))
        input_path = os.path.join(input_path, "iaf_psc_exp_multisynapse.nestml")
        nest_path = "/home/travis/nest_install"
        target_path = 'target'
        logging_level = 'INFO'
        module_name = 'nestmlmodule'
        store_log = False
        suffix = '_nestml'
        dev = True
        to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
        install_nest(target_path, nest_path)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        #
        #   network creation
        #

        neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
        nest.Connect(sg, neuron, syn_spec={"receptor_type" : 1, "weight": 1000., "delay": 0.1})

        sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
        nest.Connect(sg2, neuron, syn_spec={"receptor_type" : 2, "weight": 1000., "delay": 0.1})

        sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
        nest.Connect(sg3, neuron, syn_spec={"receptor_type" : 3, "weight": 500., "delay": 0.1})

        i_1 = nest.Create('multimeter', params={'record_from': ['I_shape__X__spikes1', 'I_shape2__X__spikes2', 'I_shape3__X__spikes3'], 'interval': 0.1})
        nest.Connect(i_1, neuron)

        vm_1 = nest.Create('voltmeter')
        nest.Connect(vm_1, neuron)


        #
        #   simulate
        #

        nest.Simulate(125.)

        #
        #   analysis
        #

        vm_1 = nest.GetStatus(vm_1)[0]["events"]
        i_1 = nest.GetStatus(i_1)[0]["events"]

        if TEST_PLOTS:

            fig, ax = plt.subplots(nrows=4)

            ax[0].plot(vm_1["times"], vm_1["V_m"], label="V_m")
            ax[0].set_ylabel("voltage")

            ax[1].plot(i_1["times"], i_1["I_shape__X__spikes1"], label="I_shape")
            ax[1].set_ylabel("current")

            ax[2].plot(i_1["times"], i_1["I_shape2__X__spikes2"], label="I_shape2")
            ax[2].set_ylabel("current")

            ax[3].plot(i_1["times"], i_1["I_shape3__X__spikes3"], label="I_shape3")
            ax[3].set_ylabel("current")

            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.set_xlim(0., 125.)
                _ax.grid(True)

            for _ax in ax[:-1]:
                _ax.set_xticklabels([])

            ax[-1].set_xlabel("time")

            fig.savefig("/tmp/nestml_multisynapse_test.png", dpi=150)

        print("Sampled values: ")
        print("\tI_shape__X__spikes1 = " + str(i_1["I_shape__X__spikes1"][220]))
        print("\tI_shape2__X__spikes2 = " + str(i_1["I_shape2__X__spikes2"][620]))
        print("\tI_shape3__X__spikes3 = " + str(i_1["I_shape3__X__spikes3"][400]))

        print("Checking for numerical match...")
        assert(np.abs(i_1["I_shape__X__spikes1"][220] - 0.04539992976248486) < 1E-9)
        assert(np.abs(i_1["I_shape2__X__spikes2"][620] - 367.8961428722326) < 1E-9)
        assert(np.abs(i_1["I_shape3__X__spikes3"][400] - -303.265329856317) < 1E-9)


if __name__ == '__main__':
    unittest.main()
