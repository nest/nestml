# -*- coding: utf-8 -*-
#
# test_neuron_build_and_sim_analytic.py
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
import unittest

from pynestml.frontend.pynestml_frontend import generate_python_standalone_target


class TestPythonStandaloneNeuronBuildAndSimAnalytic(unittest.TestCase):
    """
    Tests the code generation and running a little simulation for the iaf_psc_exp neuron, which uses only the analytic (and not a numeric) solver.

    The test asserts that the numerical membrane voltage over the course of the simulation is close to a reference timeseries obtained from NEST Simulator.
    """

    def test_python_standalone_neuron_build_and_sim_analytic(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
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

        from nestmlmodule.test_python_standalone_module import TestSimulator
        neuron_log = TestSimulator().test_simulator()
        # compare against the reference timeseries obtained by running the same model and simulation in NEST Simulator; see ``resources/generate_nest_reference_values.py``
        ref_V_m = np.loadtxt(os.path.join(os.path.dirname(__file__), "resources", "iaf_psc_exp_neuron.csv"), delimiter=",", skiprows=1, usecols=1)    # column 0: time [ms], column 1: V_m [mV]
        np.testing.assert_allclose(neuron_log["V_m"], ref_V_m, atol=1E-9)    # [mV]
