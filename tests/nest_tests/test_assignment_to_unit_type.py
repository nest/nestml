# -*- coding: utf-8 -*-
#
# test_assignment_to_unit_type.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestAssignmentToUnitType:
    """Sanity test for several predefined maths functions: log10(), ln(), erf(), erfc()"""

    def test_math_function(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "CoCoAssignmentToUnitTypeAlt.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        nrn = nest.Create("CoCoAssignmentToUnitTypeAlt_neuron_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["V"]})

        nest.Connect(mm, nrn)

        nest.Simulate(100.)

        V_log = mm.get("events")["V"]

        np.testing.assert_allclose(V_log[-1], 1000.)
