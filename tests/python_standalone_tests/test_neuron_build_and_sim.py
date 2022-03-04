# -*- coding: utf-8 -*-
#
# test_neuron_build_and_sim.py
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
import pytest
import unittest

import nest

from pynestml.frontend.pynestml_frontend import generate_python_standalone_target


class TestPythonStandaloneNeuronBuildAndSim(unittest.TestCase):
    """
    Tests the code generation and running a little simulation with NEST
    """

    def test_python_standalone_neuron_build_and_sim(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp.nestml"))))
        target_path = "nestmlmodule"
        logging_level = "INFO"
        suffix = ""
        module_name = "nestmlmodule"
        codegen_opts = {}

        generate_python_standalone_target(input_path, target_path,
                                          module_name=module_name,
                                          logging_level=logging_level,
                                          suffix=suffix,
                                          codegen_opts=codegen_opts)

        from nestmlmodule.simulator import Simulator
        from nestmlmodule.iaf_psc_exp import Neuron_iaf_psc_exp
        n = Neuron_iaf_psc_exp()
        sim = Simulator(n)
        sim.run()
