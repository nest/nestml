# -*- coding: utf-8 -*-
#
# test_on_receive_vector_input_ports.py
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
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestOnReceiveVectorInputPorts:

    def test_multisynapse_with_vector_input_ports(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "onreceive_vector_input_ports_neuron.nestml")))
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
        neuron = nest.Create("onreceive_vector_input_ports_neuron_nestml")

        # List of receptor types for the spiking input ports
        receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

        sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
        nest.Connect(sg, neuron, syn_spec={"receptor_type": receptor_types["SPIKES_0"], "weight": 1000., "delay": 0.1})

        sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
        nest.Connect(sg2, neuron, syn_spec={"receptor_type": receptor_types["SPIKES_1"], "weight": 1000., "delay": 0.1})

        mm = nest.Create("multimeter", params={"record_from": ["x", "y", "z"], "interval": nest.resolution})
        nest.Connect(mm, neuron)

        # simulate
        nest.Simulate(125.)

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3)

            ax[0].plot(mm.events["times"], mm.events["x"], label="x")
            ax[0].set_ylabel("voltage")

            ax[1].plot(mm.events["times"], mm.events["y"], label="y")
            ax[1].set_ylabel("current")

            ax[2].plot(mm.events["times"], mm.events["z"], label="z")
            ax[2].set_ylabel("current")

            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.set_xlim(0., 125.)
                _ax.grid(True)

            for _ax in ax[:-1]:
                _ax.set_xticklabels([])

            ax[-1].set_xlabel("time")

            fig.savefig("/tmp/test_onreceive_vector_input_ports.png")

        # testing
        np.testing.assert_almost_equal(mm.events["x"][-1], 4)
        np.testing.assert_almost_equal(mm.events["y"][-1], 2)
        np.testing.assert_almost_equal(mm.events["z"][-1], 2)
