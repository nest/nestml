# -*- coding: utf-8 -*-
#
# test_iaf_exp_istep.py
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
import os.path

import nest
import numpy as np
import pytest
from pynestml.codegeneration.nest_tools import NESTTools

from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
def test_iaf_psc_exp_istep():
    """
    A test for iaf_psc_exp model with step current defined inside the model
    """
    target_path = "target_iaf_istep"
    module_name = "nestml_module"
    input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "iaf_cond_exp_Istep.nestml"))
    generate_nest_target(input_path=input_path,
                         target_path=target_path,
                         logging_level="INFO",
                         module_name=module_name)
    nest.Install(module_name)
    I_step = [10., -20., 30., -40., 50.]
    t_step = [10., 30., 40., 45., 50.]
    n = nest.Create('iaf_cond_exp_Istep', params={'n_step': 5, 'I_step': I_step,
                                                  't_step': t_step})
    vm = nest.Create('voltmeter', params={'interval': 0.1})
    nest.Connect(vm, n)
    nest.Simulate(100)
    index = int(t_step[0] / nest.resolution) + 2  # +2 to wait for the raise in amplitude of V_m after the current is applied at t_step = 10ms
    np.testing.assert_allclose(vm.get("events")["V_m"][index], -69.996013)
