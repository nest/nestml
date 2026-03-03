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
    def test_nest_desktop_code_generator(self):
        """
        Test to generate the json file for NEST Desktop target for the given neuron model
        """
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
        target_path = "nest_desktop_module"
        target_platform = "NEST_DESKTOP"
        generate_target(input_path=input_path,
                        target_path=target_path,
                        target_platform=target_platform,
                        module_name=target_path,
                        logging_level="DEBUG")

        # Read the parameters from the generated json file and match them with the actual values
        with open(os.path.join(target_path, "iaf_psc_exp_neuron.json")) as f:
            data = f.read()
        json_data = json.loads(data)
        actual_params = {"C_m": "250",
                         "tau_m": "10",
                         "tau_syn_inh": "2",
                         "tau_syn_exc": "2",
                         "refr_T": "2",
                         "E_L": "-70",
                         "V_reset": "-70",
                         "V_th": "-55",
                         "I_e": "0"}
        actual_state = {
            "I_syn_exc": "0",
            "I_syn_inh": "0",
            "V_m": "-70",
            "refr_t": "0"
        }
        for recordables_data in json_data["params"]:
            _id = recordables_data["id"]
            assert recordables_data["value"] == actual_params[_id]

        for recordables_data in json_data["recordables"]:
            _id = recordables_data["id"]
            assert recordables_data["value"] == actual_state[_id]
