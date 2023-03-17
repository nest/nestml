# -*- coding: utf-8 -*-
#
# test_time_variable.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestTimeVariable:
    """Sanity test for the predefined variable ``t``, which represents simulation time"""

    def test_time_variable(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariableNeuron.nestml"))),
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest_version = NESTTools.detect_nest_version()

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install(module_name)

        nrn = nest.Create("time_variable_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["x", "y"]})
        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        if nest_version.startswith("v2"):
            timevec = nest.GetStatus(mm, "events")[0]["times"]
            x = nest.GetStatus(mm, "events")[0]["x"]
            y = nest.GetStatus(mm, "events")[0]["y"]
        else:
            timevec = mm.get("events")["times"]
            x = mm.get("events")["x"]
            y = mm.get("events")["y"]

        np.testing.assert_allclose(1E-3 * x, y)
        np.testing.assert_allclose(x, timevec - 1)
