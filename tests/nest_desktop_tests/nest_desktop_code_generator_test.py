# -*- coding: utf-8 -*-
#
# nest_desktop_code_generator_test.py
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
import json
import os
import pytest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_target


class TestNestDesktopCodeGenerator:
    """
    Test for NEST-Desktop code generator
    """

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_nest_desktop_code_generator(self):
        """
        Test to generate the json file for NEST Desktop target for the given neuron model
        """
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
        target_path = "target_nest_desktop"
        target_platform = "NEST_DESKTOP"
        generate_target(input_path=input_path,
                        target_path=target_path,
                        target_platform=target_platform,
                        logging_level="INFO")

        # Read the parameters from the generated json file and match them with the actual values
        with open(os.path.join(target_path, "iaf_psc_exp_neuron.json")) as f:
            data = f.read()
        json_data = json.loads(data)
        actual_params = {"C_m": "250.0",
                         "tau_m": "10.0",
                         "tau_syn_inh": "2.0",
                         "tau_syn_exc": "2.0",
                         "refr_T": "2.0",
                         "E_L": "-70.0",
                         "V_reset": "-70.0",
                         "V_th": "-55.0",
                         "I_e": "0.0"}
        for param_data in json_data["params"]:
            _id = param_data["id"]
            assert param_data["value"] == actual_params[_id]
