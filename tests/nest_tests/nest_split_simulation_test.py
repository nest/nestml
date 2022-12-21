# -*- coding: utf-8 -*-
#
# nest_split_simulation_test.py
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
import pytest
import unittest

import nest

from pynestml.codegeneration.nest_tools import NESTTools


try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class NestSplitSimulationTest(unittest.TestCase):
    """
    Check that nest.Simulate(100) yields the same behaviour as calling nest.Simulate(50) twice in a row.

    N.B. simulation resolution is not allowed to be changed by NEST between the two calls in the split condition.
    """

    def run_simulation(self, T_sim: float, split: bool):
        neuron_model_name = "iaf_psc_exp"

        spike_times = np.arange(10, 100, 9).astype(float)
        np.random.seed(0)
        spike_weights = np.sign(np.random.rand(spike_times.size) - .5)

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": .1})
        neuron = nest.Create(neuron_model_name)

        spikegenerator = nest.Create('spike_generator',
                                     params={'spike_times': spike_times, 'spike_weights': spike_weights})

        nest.Connect(spikegenerator, neuron)

        multimeter = nest.Create('multimeter')

        multimeter.set({"record_from": ['V_m']})

        nest.Connect(multimeter, neuron)

        if split:
            nest.Simulate(T_sim / 2.)
            nest.Simulate(T_sim / 2.)
        else:
            nest.Simulate(T_sim)

        ts = multimeter.get("events")["times"]
        Vms = multimeter.get("events")['V_m']

        if TEST_PLOTS:
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(ts, Vms, label='V_m')
            for _ax in ax:
                _ax.legend(loc='upper right')
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_split_simulation_test_[T_sim=" + str(T_sim) + "]_[split=" + str(split) + "].png")

        return ts, Vms

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_nest_split_simulation(self):
        ts, Vms = self.run_simulation(T_sim=100., split=False)
        ts_split, Vms_split = self.run_simulation(T_sim=100., split=True)
        np.testing.assert_allclose(Vms, Vms_split)
