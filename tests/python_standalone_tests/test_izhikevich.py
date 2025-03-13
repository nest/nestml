# -*- coding: utf-8 -*-
#
# test_izhikevich.py
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

from pynestml.frontend.pynestml_frontend import generate_python_standalone_target


class TestPythonStandaloneIzhikevich:
    """
    Tests the code generation and running a little simulation.
    """

    def test_python_standalone_izhikevich(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "izhikevich_neuron.nestml"))))
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        suffix = ""
        module_name = "nestmlmodule"
        codegen_opts = {}

        generate_python_standalone_target(input_path, target_path,
                                          module_name=module_name,
                                          logging_level=logging_level,
                                          suffix=suffix,
                                          codegen_opts=codegen_opts)

        from nestmlmodule.test_python_standalone_module import TestSimulator
        neuron_log = TestSimulator().test_simulator()
        np.testing.assert_allclose(neuron_log["V_m"][-1], -96.427807)
