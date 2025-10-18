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
import os

import nest
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapseNumericSolver:
    """
    Tests a synapse with non-linear dynamics requiring a numeric solver for ODEs.
    """

    def lorenz_attractor_system(self, t, state, sigma, rho, beta):
        x, y, z = state
        dxdt = (sigma * (y - x))
        dydt = (x * (rho - z) - y)
        dzdt = (x * y - beta * z)
        return [dxdt, dydt, dzdt]

    def evaluate_odes_scipy(self, func, params, initial_state, spike_times, sim_time):
        """
        Evaluate ODEs using SciPy.
        """
        sol = np.empty((3, 0))
        timevec_log = []

        # integrate the ODES from one spike time to the next, until the end of the simulation.
        t_last_spike = 0.
        spike_idx = 0
        for i in np.arange(1., sim_time + 0.01, 1.0):
            if spike_idx < len(spike_times) and i == spike_times[spike_idx]:
                t_spike = spike_times[spike_idx]
                t_span = [t_last_spike, t_spike]
                # Solve using RK45
                solution = solve_ivp(
                    fun=func,
                    t_span=t_span,  # interval of integration
                    y0=initial_state,  # initial state
                    args=params,  # parameters
                    method='RK45',
                    rtol=1e-14,  # relative tolerance
                    atol=1e-14  # absolute tolerance
                )
                timevec_log.extend(solution.t)
                sol = np.hstack((sol, solution.y))
                initial_state = solution.y[:, -1]
                t_last_spike = t_spike
                spike_idx += 1

            #sol += [initial_state]

        return timevec_log, sol

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

        """generate_nest_target(input_path=input_paths,
                             target_path=target_path,
                             logging_level="INFO",
                             suffix="_nestml",
                             module_name=modulename,
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "non_linear_synapse"}],
                                           "delay_variable": {"non_linear_synapse": "d"},
                                           "weight_variable": {"non_linear_synapse": "w"},
                                           "strictly_synaptic_vars": {"non_linear_synapse": ["x", "y", "z"]}})"""
        nest.Install(modulename)

        neuron_model = "iaf_psc_exp_neuron_nestml__with_non_linear_synapse_nestml"
        synapse_model = "non_linear_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

        neuron = nest.Create(neuron_model)
        sg = nest.Create("spike_generator", params={"spike_times": spike_times})

        syn_spec = {"synapse_model": synapse_model, "gsl_abs_error_tol": 1E-14, "gsl_rel_error_tol": 1E-14}
        nest.Connect(sg, neuron, syn_spec=syn_spec)
        connections = nest.GetConnections(source=sg, synapse_model=synapse_model)

        # Get the parameter values
        sigma = connections.get("sigma")
        rho = connections.get("rho")
        beta = connections.get("beta")

        # Initial values of state variables
        inital_state = [connections.get("x"), connections.get("y"), connections.get("z")]

        # Scipy simulation
        params = (sigma, rho, beta)
        timevec_log, sol = self.evaluate_odes_scipy(self.lorenz_attractor_system, params, inital_state, spike_times, sim_time)
        sol_arr = np.array(sol)

        # NEST simulation
        x = []
        y = []
        z = []
        sim_step_size = 1.
        for i in np.arange(0., sim_time, sim_step_size):
            nest.Simulate(sim_step_size)
            syn_stats = connections.get()
            x += [syn_stats["x"]]
            y += [syn_stats["y"]]
            z += [syn_stats["z"]]

        # Plotting
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(7, 5))
            times = np.arange(0., sim_time, sim_step_size)

            ax[0].plot(times, x, label="NESTML")
            ax[0].scatter(times, x, marker='x')
            ax[0].plot(timevec_log, sol_arr[0, :], '--', label="scipy")
            #ax[0].plot(times, sol_arr[:, 0], '--', label="scipy")
            #ax[0].scatter(times, sol_arr[:, 0], marker='o')
            ax[0].set_ylabel("x")

            ax[1].plot(times, y, label="NESTML")
            ax[1].scatter(times, y, marker='x')
            ax[1].plot(timevec_log, sol_arr[1, :], '--', label="scipy")
            #ax[1].scatter(times, sol_arr[:, 1], marker='o')
            ax[1].set_ylabel("y")

            ax[2].plot(times, z, label="NESTML")
            ax[2].scatter(times, z, marker='x')
            ax[2].plot(timevec_log, sol_arr[2, :], '--', label="scipy")
            #ax[2].scatter(times, sol_arr[:, 2], marker='o')
            ax[2].set_ylabel("z")
            for _ax in ax:
                _ax.set_xlabel("time")
                _ax.scatter(spike_times, np.zeros_like(spike_times), marker='d', color='r')

            handles, labels = ax[-1].get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper center')
            plt.savefig("non_linear_synapse.png", dpi=600)
            plt.show()

        np.testing.assert_allclose(x, sol_arr[:, 0], rtol=1e-3, atol=1e-3)
        np.testing.assert_allclose(y, sol_arr[:, 1], rtol=1e-3, atol=1e-3)
        np.testing.assert_allclose(z, sol_arr[:, 2], rtol=1e-3, atol=1e-3)
