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

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), 'PrintVariables.nestml')))
nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
target_path = '../target'
logging_level = 'INFO'
module_name = 'nestmlmodule'
store_log = False
suffix = '_nestml'
dev = True

to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
install_nest(target_path, nest_path)
nest.set_verbosity("M_ALL")

nest.ResetKernel()
nest.Install(module_name)

neuron = nest.Create("print_variable_nestml")
nest.Simulate(0.1)

if os.path.exists(target_path):
    shutil.rmtree(target_path)
