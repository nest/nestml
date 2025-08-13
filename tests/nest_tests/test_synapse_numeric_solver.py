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
import pytest
from scipy.integrate import solve_ivp

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_target, generate_nest_target
import numpy as np

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
        y0 = initial_state
        sol = []

        # integrate the ODES from one spike time to the next, until the end of the simulation.
        t_last_spike = 0.
        spike_idx = 0
        for i in np.arange(1., sim_time + 0.01, 1.0):
            if spike_idx < len(spike_times) and i == spike_times[spike_idx]:
                t_spike = spike_times[spike_idx]
                t_span = (t_last_spike, t_spike)
                print("Integrating over the interval: ", t_span)
                # Solve using RK45
                solution = solve_ivp(
                    fun=func,
                    t_span=t_span,  # interval of integration
                    y0=y0,          # initial state
                    args=params,  # parameters
                    method='RK45',
                    rtol=1e-12,      # relative tolerance
                    atol=1e-12       # absolute tolerance
                )
                y0 = solution.y[:, -1]
                t_last_spike = t_spike
                spike_idx += 1

            sol += [y0]

        return sol

    def test_non_linear_synapse(self):
        nest.ResetKernel()
        nest.set_verbosity("M_WARNING")
        dt = 0.1
        nest.resolution = dt
        sim_time = 8.0
        spike_times = [3.0, 5.0, 7.0]

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
                                                                     "synapse": "non_linear_synapse"}],
                                           "delay_variable": {"non_linear_synapse": "d"},
                                           "weight_variable": {"non_linear_synapse": "w"},
                                           "strictly_synaptic_vars": {"non_linear_synapse": ["x", "y", "z"]}})
        nest.Install(modulename)

        neuron_model = "iaf_psc_exp_neuron_nestml__with_non_linear_synapse_nestml"
        synapse_model = "non_linear_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

        neuron = nest.Create(neuron_model)
        sg = nest.Create("spike_generator", params={"spike_times": spike_times})

        nest.Connect(sg, neuron, syn_spec={"synapse_model": synapse_model})
        connections = nest.GetConnections(source=sg, synapse_model=synapse_model)

        # Get the parameter values
        sigma = connections.get("sigma")
        rho = connections.get("rho")
        beta = connections.get("beta")

        # Initial values of state variables
        inital_state = [connections.get("x"), connections.get("y"), connections.get("z")]

        # Scipy simulation
        params = (sigma, rho, beta)
        sol = self.evaluate_odes_scipy(self.lorenz_attractor_system, params, inital_state, spike_times, sim_time)
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

        # TODO: Adjust tolerance
        np.testing.assert_allclose(x, sol_arr[:, 0], atol=1e-3, rtol=1e-3)
        np.testing.assert_allclose(y, sol_arr[:, 1], atol=1e-2, rtol=1e-2)
        np.testing.assert_allclose(z, sol_arr[:, 2], atol=1e-3, rtol=1e-3)
