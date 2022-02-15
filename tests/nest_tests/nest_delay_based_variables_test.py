# -*- coding: utf-8 -*-
#
# nest_delay_based_variables_test.py
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

import nest
try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel


class DelayVariablesTest(unittest.TestCase):
    """
    Tests the behavior of delay variables in differential equations.
    """
    def setUp(self):
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedFunctions.register_functions()
        PredefinedVariables.register_variables()
        SymbolTable.initialize_symbol_table(
            ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        Logger.init_logger(LoggingLevel.INFO)

    def test_equations_with_delay_vars(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources",
                                                                "DelayBasedVariables.nestml")))
        target_path = 'target_delay'
        logging_level = 'DEBUG'
        module_name = 'nestmlmodule'
        suffix = '_nestml'
        generate_nest_target(input_path=input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
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

        if TEST_PLOTS:
            plt.plot(times, u_bar_plus_delay, label='u_bar_plus(delay)')
            plt.plot(times, foo_delay, label='foo(delay)')
            plt.plot(times, u_bar_plus, label='u_bar_plus')
            plt.plot(times, foo, label='foo')
            plt.legend()
            plt.show()
