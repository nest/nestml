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
import numpy as np
from typing import List

import nest
import pytest

try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.frontend.pynestml_frontend import generate_nest_target

target_path = "target_delay"
logging_level = "DEBUG"
suffix = "_nestml"


def plot_fig(times, recordable_events_delay: dict, recordable_events: dict, filename: str):
    fig, axes = plt.subplots(len(recordable_events), 1, figsize=(7, 9), sharex=True)
    for i, recordable_name in enumerate(recordable_events_delay.keys()):
        axes[i].plot(times, recordable_events_delay[recordable_name], label=recordable_name + "(delay)")
        axes[i].plot(times, recordable_events[recordable_name], label=recordable_name)
        axes[i].set_xlabel("times")
        axes[i].set_ylabel(recordable_name)
        axes[i].legend()

    fig.savefig("/tmp/" + filename)


def run_simulation(neuron_model_name: str, module_name: str, recordables: List[str], delay: float):
    nest.set_verbosity("M_ALL")
    nest.ResetKernel()

    try:
        nest.Install(module_name)
    except BaseException:
        pass

    neuron = nest.Create(neuron_model_name)
    neuron.set({"delay": delay})

    multimeter = nest.Create("multimeter", params={"record_from": recordables})
    nest.Connect(multimeter, neuron)

    nest.Simulate(100.0)

    events = multimeter.get("events")
    times = events["times"]

    recordable_events = {}
    for recordable in recordables:
        recordable_events[recordable] = events[recordable]

    return recordable_events, times


@pytest.mark.parametrize("file_name, neuron_model_name, recordables",
                         [("DelayDifferentialEquationsWithAnalyticSolver.nestml", "dde_analytic_nestml",
                           ["u_bar_plus", "foo"]),
                          ("DelayDifferentialEquationsWithNumericSolver.nestml", "dde_numeric_nestml", ["x", "z"]),
                          ("DelayDifferentialEquationsWithMixedSolver.nestml", "dde_mixed_nestml", ["x", "z"])])
def test_dde_with_analytic_solver(file_name: str, neuron_model_name: str, recordables: List[str]):
    input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", file_name)))
    module_name = neuron_model_name + "_module"
    print("Module name: ", module_name)
    generate_nest_target(input_path=input_path,
                         target_path=target_path,
                         logging_level=logging_level,
                         module_name=module_name,
                         suffix=suffix)
    delay = 5

    # Run the simulation with delay value of 5.0 ms
    recordable_events_delay, times = run_simulation(neuron_model_name, module_name, recordables,
                                                    delay=delay)

    # Run the simulation with no delay (0 ms)
    recordable_events, times = run_simulation(neuron_model_name, module_name, recordables, delay=0)

    if TEST_PLOTS:
        plot_fig(times, recordable_events_delay, recordable_events, neuron_model_name + ".png")

    # Assert only the analytical solver case.
    # Delayed and non-delayed results for non-linear equations produce completely different results and hence it's
    # difficult to perform a direct assert.
    if neuron_model_name == "dde_analytic_nestml":
        np.testing.assert_allclose(recordable_events_delay[recordables[1]][int(delay):],
                                   recordable_events[recordables[1]][:-int(delay)])

    @pytest.fixture(scope="function", autouse=True)
    def cleanup(self):
        # Run the test
        yield

        # clean up
        import shutil
        if self.target_path:
            try:
                shutil.rmtree(self.target_path)
            except Exception:
                pass
