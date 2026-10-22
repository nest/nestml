# -*- coding: utf-8 -*-
#
# test_unit_type_fixer_visitor.py
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


class TestUnitTypeFixerVisitor:
    @pytest.fixture(autouse=True,
                    scope="session")
    def nestml_generate_target(self) -> None:
        """Generate the model code"""

        neuron_path = os.path.join(
            os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "tests",
                                          "nest_tests", "resources", "test_unit_type_fixer_visitor.nestml")))
        generate_nest_target(input_path=[neuron_path],
                             logging_level="DEBUG",
                             suffix="_nestml")

    def test_unit_type_fixer_visitor(self) -> None:
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        n = nest.Create("test_unit_type_fixer_visitor_nestml")
        nest.Simulate(100.)

        np.testing.assert_almost_equal(n.s0, 42**2)
        np.testing.assert_almost_equal(n.s1, 1)
        np.testing.assert_almost_equal(n.s2, 42**2)
        np.testing.assert_almost_equal(n.s3, 1)

        np.testing.assert_almost_equal(n.s4, 4 * 42**2)
        np.testing.assert_almost_equal(n.s5, 1)
        np.testing.assert_almost_equal(n.s6, 4 * 42**2)
        np.testing.assert_almost_equal(n.s7, 1)
