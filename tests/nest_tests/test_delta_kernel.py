# -*- coding: utf-8 -*-
#
# test_delta_kernel.py
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
class TestDeltaKernel:
    def test_delta_kernel(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "test_delta_kernel_neuron.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)

        nest.ResetKernel()
        nest.Install(module_name)
        nest.set_verbosity("M_ALL")
        nest.resolution = 1

        nest_neuron = nest.Create("iaf_psc_delta")
        nest_neuron.V_th = 1E99
        nest_neuron.V_m = 0.
        nest_neuron.E_L = 0.
        nest_neuron.V_reset = 0.

        # network construction
        neuron = nest.Create("test_delta_kernel_neuron_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [5., 25.]})
        nest.Connect(sg, neuron, syn_spec={"weight": 100., "delay": 1.})
        nest.Connect(sg, nest_neuron, syn_spec={"weight": 100., "delay": 1.})

        mm = nest.Create("multimeter", params={"record_from": ["x", "y"],
                                               "interval": nest.resolution})
        nest.Connect(mm, neuron)

        nest_mm = nest.Create("multimeter", params={"record_from": ["V_m"],
                                                    "interval": nest.resolution})
        nest.Connect(nest_mm, nest_neuron)

        # simulate
        nest.Simulate(25.)

        conn = nest.GetConnections(source=sg,
                                   target=neuron)

        conn.weight = -conn.weight

        conn = nest.GetConnections(source=sg,
                                   target=nest_neuron)

        conn.weight = -conn.weight

        nest.Simulate(25.)

        # analysis
        if TEST_PLOTS:
            fig, ax = plt.subplots(dpi=300., nrows=2)

            ax[0].plot(mm.get()["events"]["times"], mm.get()["events"]["x"], label="x")
            ax[0].plot(mm.get()["events"]["times"], mm.get()["events"]["y"], label="y")
            ax[0].plot(nest_mm.get()["events"]["times"], nest_mm.get()["events"]["V_m"], label="NEST")

            ax[1].semilogy(nest_mm.get()["events"]["times"], np.abs(nest_mm.get()["events"]["V_m"] - mm.get()["events"]["x"]), label="x")
            ax[1].semilogy(nest_mm.get()["events"]["times"], np.abs(nest_mm.get()["events"]["V_m"] - mm.get()["events"]["y"]), label="y")
            for _ax in ax:
                _ax.legend()
                _ax.grid()

            fig.savefig("/tmp/test_delta_kernel.png")

        # testing
        np.testing.assert_allclose(nest_mm.get()["events"]["V_m"], mm.get()["events"]["x"])
        np.testing.assert_allclose(nest_mm.get()["events"]["V_m"], mm.get()["events"]["y"])
