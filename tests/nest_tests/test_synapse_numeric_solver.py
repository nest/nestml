# -*- coding: utf-8 -*-
#
# test_synapse_numeric_solver.py
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

import numpy as np
import os
import pytest
from scipy.integrate import solve_ivp

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapseNumericSolver:
    """
    Tests a synapse with non-linear dynamics requiring a numeric solver for ODEs.
    """

    def lotka_volterra_system(self, t, state, alpha, beta, delta, gamma):
        x, y = state
        dxdt = (alpha * x - beta * x * y)
        dydt = (-gamma * y + delta * x * y)
        return [dxdt, dydt]

    def evaluate_odes_scipy(self, func, params, initial_state, spike_times, sim_time):
        """
        Evaluate ODEs using SciPy.
        """
        solution = solve_ivp(
            fun=func,
            t_span=[0, sim_time],  # interval of integration
            y0=initial_state,  # initial state
            args=params,  # parameters
            method="RK45",
            t_eval=np.arange(0, sim_time + 0.01, 1.0),
            rtol=1e-8,  # relative tolerance
            atol=1e-8  # absolute tolerance
        )
        return solution.y

    def test_non_linear_synapse(self):
        nest.ResetKernel()
        nest.set_verbosity("M_WARNING")
        dt = 0.1
        nest.resolution = dt
        sim_time = 30.
        spike_times = [3.0, 5.0, 9.0, 11.0, 22.0, 28.0]

        files = ["models/neurons/iaf_psc_exp_neuron.nestml", "tests/nest_tests/resources/non_linear_synapse.nestml"]
        input_paths = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "target_nl"
        modulename = "nl_syn_module"

        generate_nest_target(input_path=input_paths,
                             target_path=target_path,
                             logging_level="INFO",
                             suffix="_nestml",
                             module_name=modulename,
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapses": {"non_linear_synapse": {}}}],
                                           "delay_variable": {"non_linear_synapse": "d"},
                                           "weight_variable": {"non_linear_synapse": "w"},
                                           "strictly_synaptic_vars": {"non_linear_synapse": ["x", "y"]}})
        nest.Install(modulename)

        neuron_model = "iaf_psc_exp_neuron_nestml__with_non_linear_synapse_nestml"
        synapse_model = "non_linear_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

        neuron = nest.Create(neuron_model)
        sg = nest.Create("spike_generator", params={"spike_times": spike_times})

        syn_spec = {"synapse_model": synapse_model, "gsl_abs_error_tol": 1E-8, "gsl_rel_error_tol": 1E-8}
        nest.Connect(sg, neuron, syn_spec=syn_spec)
        connections = nest.GetConnections(source=sg, synapse_model=synapse_model)

        # Initial values of state variables
        initial_state = [connections.get("x"), connections.get("y")]

        # Scipy simulation
        params = (connections.get("alpha"), connections.get("beta"), connections.get("delta"), connections.get("gamma"))
        sol = self.evaluate_odes_scipy(self.lotka_volterra_system, params, initial_state, spike_times, sim_time)

        # Prepare the solution array to retain values between spike times.
        sol_arr = np.empty((0, 2))
        spike_index = 0
        sol = sol.T
        old_row = sol[0:1, :]
        for i in range(sol.shape[0]):
            if spike_index < len(spike_times) and i == int(spike_times[spike_index]):
                old_row = sol[i: i + 1, :]
                spike_index += 1
            sol_arr = np.vstack([sol_arr, old_row])

        # NEST simulation
        x = [initial_state[0]]
        y = [initial_state[1]]
        sim_step_size = 1.
        for i in np.arange(0., sim_time, sim_step_size):
            nest.Simulate(sim_step_size)
            syn_stats = connections.get()
            x += [syn_stats["x"]]
            y += [syn_stats["y"]]

        # Plotting
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(7, 5))
            times = np.arange(0., sim_time + 0.01, sim_step_size)

            ax[0].plot(times, x, label="NESTML")
            ax[0].scatter(times, x, marker="x")
            ax[0].plot(times, sol_arr[:, 0], "--", label="scipy")
            ax[0].scatter(times, sol_arr[:, 0], marker="o")
            ax[0].set_ylabel("x")

            ax[1].plot(times, y, label="NESTML")
            ax[1].scatter(times, y, marker="x")
            ax[1].plot(times, sol_arr[:, 1], "--", label="scipy")
            ax[1].scatter(times, sol_arr[:, 1], marker="o")
            ax[1].set_ylabel("y")

            for _ax in ax:
                _ax.set_xlabel("time")
                _ax.scatter(spike_times, np.zeros_like(spike_times), marker="d", color="r")

            handles, labels = ax[-1].get_legend_handles_labels()
            fig.legend(handles, labels, loc="upper center")
            plt.savefig("non_linear_synapse.png")

        np.testing.assert_allclose(x, sol_arr[:, 0])
        np.testing.assert_allclose(y, sol_arr[:, 1])
