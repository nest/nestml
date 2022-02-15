# -*- coding: utf-8 -*-
#
# delay_based_variables_test.py
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
import matplotlib.pyplot as plt

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources",
                                                        "DelayBasedVariables.nestml")))
nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
target_path = 'target_delay'
logging_level = 'DEBUG'
module_name = 'nestmlmodule'
store_log = False
suffix = '_nestml'
dev = True

# to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
# install_nest(target_path, nest_path)
nest.set_verbosity("M_ALL")
nest.ResetKernel()
nest.Install(module_name)

neuron = nest.Create("delay_variables_nestml")
multimeter = nest.Create("multimeter", params={"record_from": ["u_bar_plus", "foo"]})
nest.Connect(multimeter, neuron)

nest.Simulate(100.0)
events = multimeter.get("events")
times = events["times"]
u_bar_plus_delay = events["u_bar_plus"]
foo_delay = events["foo"]


# Set the delay to 0
nest.ResetKernel()
neuron = nest.Create("delay_variables_nestml")
nest.SetStatus(neuron, {"delay": 0.0})

multimeter = nest.Create("multimeter", params={"record_from": ["u_bar_plus", "foo"]})
nest.Connect(multimeter, neuron)

nest.Simulate(100.0)
events = multimeter.get("events")
times = events["times"]
u_bar_plus = events["u_bar_plus"]
foo = events["foo"]

plt.plot(times, u_bar_plus_delay, label='u_bar_plus(delay)')
plt.plot(times, foo_delay, label='foo(delay)')
plt.plot(times, u_bar_plus, label='u_bar_plus')
plt.plot(times, foo, label='foo')
plt.legend()
plt.show()

