# -*- coding: utf-8 -*-
#
# test_multiple_continuous_input_ports.py
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
import os

import nest
import numpy as np

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestMultipleInputPorts:
    """
    Tests multiple continuous input ports in NEST.
    """
    def test_multiple_continuous_input_ports(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "multiple_input_currents_neuron.nestml")))
        generate_nest_target(input_path=input_path,
                             target_path="target",
                             logging_level="INFO",
                             suffix="_nestml")
        nest.ResetKernel()
        nest.resolution = 0.1
        nest.Install("nestmlmodule")
        neuron = nest.Create("multiple_input_currents_neuron_nestml")
        continuous_inputs = nest.GetStatus(neuron, "continuous_inputs")[0]

        dc1 = nest.Create("dc_generator", params={"amplitude": 150.0})
        nest.Connect(dc1, neuron, syn_spec={'receptor_type': continuous_inputs["I_1"]})

        dc2 = nest.Create("dc_generator", params={"amplitude": 225.0})
        nest.Connect(dc2, neuron, syn_spec={'receptor_type': continuous_inputs["I_2"]})

        # multimeter{
        mm = nest.Create("multimeter", params={"record_from": ["V_m1", "V_m2"]})
        nest.Connect(mm, neuron)

        nest.Simulate(10.)

        v_m1 = nest.GetStatus(mm, "events")[0]["V_m1"]
        v_m2 = nest.GetStatus(mm, "events")[0]["V_m2"]

        print(v_m1, v_m2)

        np.testing.assert_allclose(v_m1[-1], 2370)
        np.testing.assert_allclose(v_m2[-1], 1767.5)
