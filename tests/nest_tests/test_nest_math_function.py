# -*- coding: utf-8 -*-
#
# test_nest_math_function.py
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


class TestNestMathFunction:
    """Sanity test for several predefined maths functions: log10(), ln(), erf(), erfc()"""

    def test_math_function(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "MathFunctionTest.nestml")))
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

        nrn = nest.Create("math_function_test_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["x", "ln_state", "log10_state", "erf_state", "erfc_state", "ceil_state", "floor_state", "round_state", "abs_state", "cos_state", "sin_state", "tan_state"]})

        nest.Connect(mm, nrn)

        nest.Simulate(100.)

        if nest_version.startswith("v2"):
            timevec = nest.GetStatus(mm, "events")[0]["x"]
            ln_state_ts = nest.GetStatus(mm, "events")[0]["ln_state"]
            log10_state_ts = nest.GetStatus(mm, "events")[0]["log10_state"]
            erf_state_ts = nest.GetStatus(mm, "events")[0]["erf_state"]
            erfc_state_ts = nest.GetStatus(mm, "events")[0]["erfc_state"]
            ceil_state_ts = nest.GetStatus(mm, "events")[0]["ceil_state"]
            floor_state_ts = nest.GetStatus(mm, "events")[0]["floor_state"]
            round_state_ts = nest.GetStatus(mm, "events")[0]["round_state"]
            abs_state_ts = nest.GetStatus(mm, "events")[0]["abs_state"]
            cos_state_ts = nest.GetStatus(mm, "events")[0]["cos_state"]
            sin_state_ts = nest.GetStatus(mm, "events")[0]["sin_state"]
            tan_state_ts = nest.GetStatus(mm, "events")[0]["tan_state"]
        else:
            timevec = mm.get("events")["x"]
            ln_state_ts = mm.get("events")["ln_state"]
            log10_state_ts = mm.get("events")["log10_state"]
            erf_state_ts = mm.get("events")["erf_state"]
            erfc_state_ts = mm.get("events")["erfc_state"]
            ceil_state_ts = mm.get("events")["ceil_state"]
            floor_state_ts = mm.get("events")["floor_state"]
            round_state_ts = mm.get("events")["round_state"]
            abs_state_ts = mm.get("events")["abs_state"]
            cos_state_ts = mm.get("events")["cos_state"]
            sin_state_ts = mm.get("events")["sin_state"]
            tan_state_ts = mm.get("events")["tan_state"]

        ref_ln_state_ts = np.log(timevec - 1)
        ref_log10_state_ts = np.log10(timevec - 1)
        ref_erf_state_ts = sp.special.erf(timevec - 1)
        ref_erfc_state_ts = sp.special.erfc(timevec - 1)
        ref_ceil_state_ts = np.ceil((timevec - 1) / 10)
        ref_floor_state_ts = np.floor((timevec - 1) / 10)
        ref_round_state_ts = np.round((timevec - 1) / 10)
        ref_abs_state_ts = np.abs(timevec - 1)
        ref_cos_state_ts = np.cos(timevec - 1)
        ref_sin_state_ts = np.sin(timevec - 1)
        ref_tan_state_ts = np.tan(timevec - 1)

        np.testing.assert_allclose(ln_state_ts, ref_ln_state_ts)
        np.testing.assert_allclose(log10_state_ts, ref_log10_state_ts)
        np.testing.assert_allclose(erf_state_ts, ref_erf_state_ts)
        np.testing.assert_allclose(erfc_state_ts, ref_erfc_state_ts)
        np.testing.assert_allclose(ceil_state_ts, ref_ceil_state_ts)
        np.testing.assert_allclose(floor_state_ts, ref_floor_state_ts)
        np.testing.assert_allclose(round_state_ts, ref_round_state_ts)
        np.testing.assert_allclose(abs_state_ts, ref_abs_state_ts)
        np.testing.assert_allclose(cos_state_ts, ref_cos_state_ts)
        np.testing.assert_allclose(sin_state_ts, ref_sin_state_ts)
        np.testing.assert_allclose(tan_state_ts, ref_tan_state_ts)
