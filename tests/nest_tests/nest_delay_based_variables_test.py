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
from typing import List

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

        self.target_path = 'target_delay'
        self.logging_level = 'DEBUG'
        self.module_name = 'nestmlmodule'
        self.suffix = '_nestml'

    def plot_fig(self, times, recordable_events_delay: dict, recordable_events: dict, filename: str):
        fig, axes = plt.subplots(len(recordable_events), 1, figsize=(7, 9), sharex=True)
        for i, recordable_name in enumerate(recordable_events_delay.keys()):
            axes[i].plot(times, recordable_events_delay[recordable_name], label=recordable_name + "(delay)")
            axes[i].plot(times, recordable_events[recordable_name], label=recordable_name)
            axes[i].set_xlabel("times")
            axes[i].set_ylabel(recordable_name)
            axes[i].legend()

        fig.savefig("/tmp/" + filename)

    def run_simulation(self, neuron_model_name: str, recordables: List[str], delay: float, dc_gen=False, spikes=None):
        nest.set_verbosity("M_ALL")
        nest.ResetKernel()

        try:
            nest.Install(self.module_name)
        except BaseException:
            pass

        neuron = nest.Create(neuron_model_name)
        nest.SetStatus(neuron, {"delay": delay})

        multimeter = nest.Create("multimeter", params={"record_from": recordables})
        nest.Connect(multimeter, neuron)

        if spikes is not None:
            sg = nest.Create('spike_generator', params={'spike_times': spikes})
            nest.Connect(sg, neuron)

        if dc_gen:
            cgs = nest.Create('dc_generator')
            cgs.set({"amplitude": 25.})
            nest.Connect(cgs, neuron)

        nest.Simulate(100.0)

        events = multimeter.get("events")
        times = events["times"]

        recordable_events = {}
        for recordable in recordables:
            recordable_events[recordable] = events[recordable]

        return recordable_events, times

    def test_eqns_with_delay_vars_analytic_solver(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources",
                                                                "DelayBasedVariablesWithAnalyticSolver.nestml")))
        generate_nest_target(input_path=input_path,
                             target_path=self.target_path,
                             logging_level=self.logging_level,
                             module_name=self.module_name,
                             suffix=self.suffix)
        recordables = ["u_bar_plus", "foo"]
        neuron_model_name = "delay_variables_nestml"

        # Run the simulation with delay value of 5.0 ms
        recordable_events_delay, times = self.run_simulation(neuron_model_name, recordables, delay=5.0)

        # Run the simulation with no delay (0 ms)
        recordable_events, times = self.run_simulation(neuron_model_name, recordables, delay=0.0)

        if TEST_PLOTS:
            self.plot_fig(times, recordable_events_delay, recordable_events, neuron_model_name + ".png")

    def test_equations_with_delay_vars_numerical_solver(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources",
                                                                "DelayBasedVariablesWithNumericalSolver.nestml")))
        generate_nest_target(input_path=input_path,
                             target_path=self.target_path,
                             logging_level=self.logging_level,
                             module_name=self.module_name,
                             suffix=self.suffix)
        recordables = ["V_m", "U_m"]
        neuron_model_name = "izhikevich_delay_nestml"

        # Run simulation with delay
        recordable_events_delay, times = self.run_simulation(neuron_model_name,
                                                             recordables,
                                                             delay=5.0, dc_gen=True)

        # Run the simulation with no delay
        recordable_events, times = self.run_simulation(neuron_model_name,
                                                       recordables,
                                                       delay=0.0, dc_gen=True)

        if TEST_PLOTS:
            self.plot_fig(times, recordable_events_delay, recordable_events, neuron_model_name + ".png")

    def test_equations_with_delay_vars_mixed_solver(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources",
                                                                "DelayBasedVariablesWithMixedSolver.nestml"))),
        generate_nest_target(input_path=input_path,
                             target_path=self.target_path,
                             logging_level=self.logging_level,
                             module_name=self.module_name,
                             suffix=self.suffix)
        recordables = ["V_m", "w"]
        neuron_model_name = "delay_variables_mixed_solver_nestml"
        spikes = [1.0, 1.0, 1.5, 1.5, 6.7, 10.0, 10.5, 10.5, 10.5, 10.5, 11.3, 11.3, 11.4, 11.4, 20., 22.5, 30.,
                  40., 42., 42., 42., 50.5, 50.5, 75., 88., 93., 95., 96.7, 98.8]

        # Simulate with delay
        recordable_events_delay, times = self.run_simulation(neuron_model_name,
                                                             recordables,
                                                             delay=45.0, spikes=spikes)

        # Simulate without delay
        recordable_events, times = self.run_simulation(neuron_model_name,
                                                       recordables,
                                                       delay=0., spikes=spikes)

        if TEST_PLOTS:
            self.plot_fig(times, recordable_events_delay, recordable_events, neuron_model_name + ".png")
