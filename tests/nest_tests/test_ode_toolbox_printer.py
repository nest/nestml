# -*- coding: utf-8 -*-
#
# test_ode_toolbox_printer.py
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


class TestODEToolboxprinter:
    r"""Test a parrot neuron that repeats all spikes received on its first input port. This tests that spikes can be emitted from inside onReceive blocks."""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""
        files = [os.path.join("tests", "nest_tests", "resources", "ode_toolbox_printer_test.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml")

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_ode_toolbox_printer(self):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        neuron = nest.Create("ode_toolbox_printer_test_nestml")
        mm = nest.Create("multimeter", params={"record_from": ["I_syn"]})
        nest.Connect(mm, neuron)

        nest.Simulate(35.)
        I_syn = mm.get("events")["I_syn"]
        np.testing.assert_allclose(I_syn[-1], 4.45069954)
