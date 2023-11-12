# -*- coding: utf-8 -*-
#
# test_forward_euler_integrator.py
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


class TestForwardEulerIntegrator:
    """
    Tests the forward Euler integrator by comparing it to RK45.
    """

    def generate_target(self, numeric_solver: str):
        r"""Generate the neuron model code"""

        files = [os.path.join("models", "neurons", "izhikevich_neuron.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_" + numeric_solver.replace("-", "_") + "_nestml",
                             module_name="nestml" + numeric_solver.replace("-", "_") + "module",
                             codegen_opts={"numeric_solver": numeric_solver})

        nest.Install("nestml" + numeric_solver.replace("-", "_") + "module")

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_forward_euler_integrator(self):
        self.generate_target("forward-Euler")
        self.generate_target("rk45")

        nest.ResetKernel()
        nest.resolution = .001

        nrn1 = nest.Create("izhikevich_neuron_rk45_nestml")
        nrn2 = nest.Create("izhikevich_neuron_forward_Euler_nestml")

        nrn1.I_e = 10.
        nrn2.I_e = 10.

        mm1 = nest.Create("multimeter")
        mm1.set({"record_from": ["V_m"]})

        mm2 = nest.Create("multimeter")
        mm2.set({"record_from": ["V_m"]})

        nest.Connect(mm1, nrn1)
        nest.Connect(mm2, nrn2)

        nest.Simulate(100.)

        v_m1 = mm1.get("events")["V_m"]
        v_m2 = mm2.get("events")["V_m"]

        np.testing.assert_allclose(v_m1, v_m2, atol=2, rtol=0)       # allow max 2 mV difference between the solutions
