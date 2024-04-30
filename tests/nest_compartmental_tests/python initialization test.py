# -*- coding: utf-8 -*-
#
# python initialization test.py
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

import os
import unittest

import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestNonExistingParamReject(unittest.TestCase):
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "cm_default.nestml"
        )
        target_path = os.path.join(
            tests_path,
            "target/"
        )

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(
            f"Compiled nestml model 'cm_main_cm_default_nestml' not found, installing in:"
            f"    {target_path}"
        )

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path="/tmp/nestml-component/",
            module_name="cm_default_module",
            suffix="_nestml",
            logging_level="DEBUG"
        )

        nest.Install("cm_default_module.so")

    def test_non_existing_param(self):
        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1., 'e_L': -70.0, 'non_existing': 1.0}

        with pytest.raises(nest.NESTErrors.BadParameter):
            cm = nest.Create('cm_default_nestml')
            cm.compartments = [{"parent_idx": -1, "params": params}]

    def test_existing_param(self):
        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1., 'e_L': -70.0, 'gbar_Na': 1.0}

        cm = nest.Create('cm_default_nestml')
        cm.compartments = [{"parent_idx": -1, "params": params}]
