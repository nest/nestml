# -*- coding: utf-8 -*-
#
# test__cse_ca_argument_regression.py
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

import datetime
import os
import re

import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target


class TestCSECaArgumentRegression:
    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "concmech.nestml")

        gen_name = "TestCSECaArgumentRegression_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target_path = os.path.join(tests_path, "target", gen_name)
        os.makedirs(target_path, exist_ok=True)

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path=target_path,
            module_name="cse_ca_argument_regression_module",
            suffix="_nestml",
            logging_level="INFO",
        )

        request.cls.target_path = target_path
        request.cls.generated_cpp = os.path.join(
            target_path,
            "cm_neuroncurrents_multichannel_test_model_nestml.cpp",
        )
        request.cls.module_filename = "cse_ca_argument_regression_module.so"

    def test_cse_preserves_ca_function_argument(self):
        assert os.path.exists(self.generated_cpp), f"Generated source not found: {self.generated_cpp}"

        with open(self.generated_cpp, "r", encoding="utf-8") as f:
            code = f.read()

        block_match = re.search(
            r"auto z_inf_SK_E2 = \[\]\(.*?\)\s*\{.*?return val;\s*\};",
            code,
            flags=re.DOTALL,
        )
        assert block_match is not None, "z_inf_SK_E2 function block not found in generated C++."
        block = block_match.group(0)

        assert "315576000.0" not in block, "Unit constant leaked into z_inf_SK_E2 instead of function argument."
        assert re.search(r"\bca\b", block) is not None, "Expected function argument 'ca' missing in z_inf_SK_E2."

    def test_cse_regression_model_runs(self):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))
        nest.Install(self.module_filename)

        cm = nest.Create("multichannel_test_model_nestml")
        cm.compartments = [
            {"parent_idx": -1, "params": {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}},
        ]
        cm.receptors = [{"comp_idx": 0, "receptor_type": "AMPA"}]

        mm = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": 0.1})
        nest.Connect(mm, cm)
        nest.Simulate(1.1)

        events = nest.GetStatus(mm, "events")[0]
        assert len(events["v_comp0"]) > 0, "No voltage samples recorded from generated regression model."
