# -*- coding: utf-8 -*-
#
# test_division.py
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
import scipy as sp
import os

from pynestml.frontend.pynestml_frontend import generate_nest_target, generate_python_standalone_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestDivision:
    """Test integer and floating point division"""

    def test_division_function_nest(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "integer_division.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        NESTTools.set_nest_verbosity("ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.resolution = 1.    # [ms]
        nest.Install("nestmlmodule")

        nrn = nest.Create("integer_division_test_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["x", "y", "z", "p", "q", "r", "neg1", "neg2", "neg3"]})

        nest.Connect(mm, nrn)

        nest.Simulate(2.)

        np.testing.assert_allclose(mm.get("events")["x"], 2)    # integer division of an integer
        np.testing.assert_allclose(mm.get("events")["y"], np.pi / 2)
        np.testing.assert_allclose(mm.get("events")["z"], int(np.pi / 2))
        np.testing.assert_allclose(mm.get("events")["p"], np.pi / 2)
        np.testing.assert_allclose(mm.get("events")["q"], np.pi / 2)
        np.testing.assert_allclose(mm.get("events")["r"], 2)
        np.testing.assert_allclose(mm.get("events")["neg1"], -2)    # N.B. Python would give -3 here, but we want C-style integer division
        np.testing.assert_allclose(mm.get("events")["neg2"], -2)    # N.B. Python would give -3 here, but we want C-style integer division
        np.testing.assert_allclose(mm.get("events")["neg3"], 2)

    def test_division_function_python(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "integer_division.nestml")))
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_python_standalone_target(input_path, target_path,
                                          module_name=module_name,
                                          logging_level=logging_level,
                                          suffix=suffix)

        from nestmlmodule.test_python_standalone_module import TestSimulator
        neuron_log = TestSimulator().test_simulator(.1)

        np.testing.assert_allclose(neuron_log["x"][0], 2)    # integer division of an integer
        np.testing.assert_allclose(neuron_log["y"][0], np.pi / 2)
        np.testing.assert_allclose(neuron_log["z"][0], int(np.pi / 2))
        np.testing.assert_allclose(neuron_log["p"][0], np.pi / 2)
        np.testing.assert_allclose(neuron_log["q"][0], np.pi / 2)
        np.testing.assert_allclose(neuron_log["r"][0], 2)
        np.testing.assert_allclose(neuron_log["neg1"][0], -2)    # N.B. Python would give -3 here, but we want C-style integer division
        np.testing.assert_allclose(neuron_log["neg2"][0], -2)    # N.B. Python would give -3 here, but we want C-style integer division
        np.testing.assert_allclose(neuron_log["neg3"][0], 2)
