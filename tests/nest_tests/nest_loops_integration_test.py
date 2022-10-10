# -*- coding: utf-8 -*-
#
# nest_loops_integration_test.py
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
import unittest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


class NestLoopsIntegrationTest(unittest.TestCase):
    """
    Tests the code generation and working of for and while loops from NESTML to NEST
    """

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_for_and_while_loop(self):
        files = ["ForLoop.nestml", "WhileLoop.nestml"]
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", s))) for s in
                      files]
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

        nrn = nest.Create("for_loop_nestml")
        mm = nest.Create("multimeter")
        mm.set({"record_from": ["V_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(5.0)

        v_m = mm.get("events")["V_m"]
        np.testing.assert_almost_equal(v_m[-1], 16.6)

        nest.ResetKernel()
        nrn = nest.Create("while_loop_nestml")

        mm = nest.Create("multimeter")
        mm.set({"record_from": ["y"]})

        nest.Connect(mm, nrn)

        nest.Simulate(5.0)
        y = mm.get("events")["y"]
        np.testing.assert_almost_equal(y[-1], 5.011)
