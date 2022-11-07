# -*- coding: utf-8 -*-
#
# print_variable_script.py
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
import nest
import shutil

from pynestml.frontend.pynestml_frontend import generate_nest_target

input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), "PrintVariables.nestml")))
target_path = "target"
logging_level = "INFO"
module_name = "nestmlmodule"
suffix = "_nestml"

generate_nest_target(input_path,
                     target_path=target_path,
                     logging_level=logging_level,
                     module_name=module_name,
                     suffix=suffix)
nest.set_verbosity("M_ALL")

nest.ResetKernel()
nest.Install(module_name)

neuron = nest.Create("print_variable_nestml")
nest.Simulate(0.1)

if os.path.exists(target_path):
    shutil.rmtree(target_path)
