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

from pynestml.frontend.pynestml_frontend import generate_nest_target


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
                         module_name=module_name,
                         suffix="_nestml")
    nest.Install(module_name)
