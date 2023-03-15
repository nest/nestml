# -*- coding: utf-8 -*-
#
# nest_logarithmic_function_test.py
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
from pynestml.codegeneration.nest_tools import NESTTools


class NestLogarithmicFunctionTest(unittest.TestCase):
    """Sanity test for the predefined logarithmic functions ln() and log10()"""

    def test_logarithmic_function(self):
        MAX_SSE = 1E-12

        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "LogarithmicFunctionTest.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "LogarithmicFunctionTest_invalid.nestml")))]
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
        nest.Install("nestmlmodule")

        nrn = nest.Create("logarithm_function_test_nestml")
        mm = nest.Create("multimeter")

        ln_state_specifier = "ln_state"
        log10_state_specifier = "log10_state"
        nest.SetStatus(mm, {"record_from": [ln_state_specifier, log10_state_specifier, "x"]})

        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        if nest_version.startswith("v2"):
            timevec = nest.GetStatus(mm, "events")[0]["x"]
            ln_state_ts = nest.GetStatus(mm, "events")[0][ln_state_specifier]
            log10_state_ts = nest.GetStatus(mm, "events")[0][log10_state_specifier]
        else:
            timevec = mm.get("events")["x"]
            ln_state_ts = mm.get("events")[ln_state_specifier]
            log10_state_ts = mm.get("events")[log10_state_specifier]
        ref_ln_state_ts = np.log(timevec - 1)
        ref_log10_state_ts = np.log10(timevec - 1)

        assert np.all((ln_state_ts - ref_ln_state_ts)**2 < MAX_SSE)
        assert np.all((log10_state_ts - ref_log10_state_ts)**2 < MAX_SSE)

        # test that expected failure occurs

        nest.ResetKernel()
        nrn = nest.Create("logarithm_function_test_invalid_nestml")

        mm = nest.Create("multimeter")

        ln_state_specifier = "ln_state"
        log10_state_specifier = "log10_state"
        nest.SetStatus(mm, {"record_from": [ln_state_specifier, log10_state_specifier, "x"]})

        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        if nest_version.startswith("v2"):
            timevec = nest.GetStatus(mm, "events")[0]["times"]
            ln_state_ts = nest.GetStatus(mm, "events")[0][ln_state_specifier]
            log10_state_ts = nest.GetStatus(mm, "events")[0][log10_state_specifier]
        else:
            timevec = mm.get("events")["times"]
            ln_state_ts = mm.get("events")[ln_state_specifier]
            log10_state_ts = mm.get("events")[log10_state_specifier]
        ref_ln_state_ts = np.log(timevec - 1)
        ref_log10_state_ts = np.log10(timevec - 1)

        assert not np.all((ln_state_ts - ref_ln_state_ts)**2 < MAX_SSE)
        assert not np.all((log10_state_ts - ref_log10_state_ts)**2 < MAX_SSE)
