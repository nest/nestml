# -*- coding: utf-8 -*-
#
# nest_forbidden_variable_names_test.py
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
import unittest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class NestForbiddenVariableNamesTest(unittest.TestCase):
    r"""Test rewriting of forbidden variable names: in the case of NEST, C++ language keywords."""

    def test_forbidden_variable_names(self):
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "CppVariableNames.nestml")))]
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
        nest.Install("nestmlmodule")

        nrn = nest.Create("cpp_variable_names_test_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["concept_", "static_"]})
        nest.Connect(mm, nrn)
        nest.Simulate(100.0)
        nest.SetStatus(nrn, {"using_": 42.})

        # getting here without exceptions means that the test has passed
