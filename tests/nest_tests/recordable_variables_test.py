# -*- coding: utf-8 -*-
#
# recordable_variables_test.py
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
import unittest
import os
import nest
import numpy as np

from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class RecordableVariablesTest(unittest.TestCase):
    """
    Test to check the recordable variables: from state and initial_values block and inline expressions in the equations block
    """

    def test_recordable_variables(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "RecordableVariables.nestml")))
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install(module_name)

        neuron = nest.Create("recordable_variables_nestml")
        sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
        nest.Connect(sg, neuron)

        mm = nest.Create('multimeter', params={'record_from': ['V_ex', 'V_m', 'V_abs', 'I_kernel__X__spikes'],
                                               'interval': 0.1})
        nest.Connect(mm, neuron)

        nest.Simulate(100.)

        # Get the recordable variables
        events = nest.GetStatus(mm)[0]["events"]
        V_reset = nest.GetStatus(neuron, "V_reset")
        V_m = events["V_m"]
        self.assertIsNotNone(V_m)

        V_abs = events["V_abs"]
        self.assertIsNotNone(V_abs)

        np.testing.assert_allclose(V_m, V_abs + V_reset)

        V_ex = events["V_ex"]
        np.testing.assert_almost_equal(V_ex[-1], -10)
