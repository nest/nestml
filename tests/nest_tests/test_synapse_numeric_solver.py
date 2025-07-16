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

    def test_synapse_with_numeric_solver(self):
        nest.ResetKernel()
        nest.set_verbosity("M_WARNING")
        dt = 0.1
        nest.resolution = dt

        files = ["models/neurons/iaf_psc_exp_neuron.nestml", "tests/nest_tests/resources/stp_synapse.nestml"]
        input_paths = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "target_stp"
        modulename = "stp_module"

        generate_nest_target(input_path=input_paths,
                             target_path=target_path,
                             logging_level="INFO",
                             suffix="_nestml",
                             module_name=modulename,
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "stp_synapse"}],
                                           "delay_variable": {"stp_synapse": "d"},
                                           "weight_variable": {"stp_synapse": "w"}})
        nest.Install(modulename)

        # properties of the generated spike train
        frequency = 50  # in Hz
        spike_count = 10
        step = 1000. / frequency  # in ms
        duration = spike_count * step
        sim_time = duration + 11_000

        spike_times = (([i * step for i in range(1, spike_count + 1)]  # 10 spikes at 50Hz
                        + [duration + 500])  # then 500ms after
                       + [duration + 10_000])  # then 10s after

        # parameters for the spike generator (spike train injector)
        params_sg = {
            "spike_times": spike_times
        }
        print(spike_times)
        neuron_model = "iaf_psc_exp_neuron_nestml__with_stp_synapse_nestml"
        synapse_model = "stp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

        print("Creating the neuron model")
        neuron = nest.Create(neuron_model)

        print("Creating spike generator")
        spike_train_injector = nest.Create("spike_train_injector", params=params_sg)

        voltmeter = nest.Create("voltmeter", params={'interval': 0.1})
        spike_recorder = nest.Create("spike_recorder")

        print("Connecting the synapse")
        nest.Connect(spike_train_injector, neuron, syn_spec={"synapse_model": synapse_model})
        nest.Connect(voltmeter, neuron)
        nest.Connect(spike_train_injector, spike_recorder)
        connections = nest.GetConnections(source=spike_train_injector, synapse_model=synapse_model)
        x = []
        u = []
        U = []
        sim_step_size = 1.
        for i in np.arange(0., sim_time + 0.01, sim_step_size):
            nest.Simulate(sim_step_size)
            syn_stats = connections.get()  # nest.GetConnections()[2].get()
            x += [syn_stats["x"]]
            u += [syn_stats["u"]]
            U += [syn_stats["U"]]

        data_vm = voltmeter.events
        data_sr = spike_recorder.events

        # TODO: add assertions

        if TEST_PLOTS:
            fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 15))

            ax[0].vlines(data_sr["times"], 0, 1)
            ax[0].set_xlim([0, sim_time])
            ax[0].set_xlabel('Time (s)')

            ax[1].set_xlim([0, sim_time])
            ax[1].set_ylim([0, 1])
            ax[1].set_xlabel('Time (s)')

            ax[1].plot(x, label='x')
            ax[1].plot(u, label='u')
            ax[1].plot(U, label='U')
            ax[1].legend(loc='best')

            ax[2].set_xlim([0, sim_time])
            ax[2].set_xlabel('Time (ms)')

            for ax_ in ax:
                ax_.set_xlim([1., sim_time])
                ax_.set_xscale('log')

            ax[2].plot(data_vm["times"], data_vm["V_m"])

            fig.tight_layout()
            fig.savefig('synaug_numsim.pdf')

    def lorenz_attractor_system(self, t, state, sigma, rho, beta):
        x, y, z = state
        dxdt = (sigma * (y - x))
        dydt = (x * (rho - z) - y)
        dzdt = (x * y - beta * z)
        return [dxdt, dydt, dzdt]

    def evaluate_odes_scipy(self, sigma, rho, beta, initial_state, spike_times, sim_time):
        x_arr = []
        y_arr = []
        z_arr = []
        y0 = initial_state

        t_last_spike = 0.
        spike_idx = 0
        for i in np.arange(1., sim_time + 0.01, 1.0):
            if spike_idx < len(spike_times) and i == spike_times[spike_idx]:
                t_spike = spike_times[spike_idx]
                t_span = (t_last_spike, t_spike)
                print("Integrating over the iterval: ", t_span)
                # Solve using RK45
                solution = solve_ivp(
                    fun=self.lorenz_attractor_system,
                    t_span=t_span,
                    y0=y0,  # [x_arr[-1], y_arr[-1], z_arr[-1]],
                    args=(sigma, rho, beta),
                    method='RK45',
                    first_step=0.1,
                    rtol=1e-6,  # relative tolerance
                    atol=1e-6  # absolute tolerance
                )
                y0 = solution.y[:, -1]
                t_last_spike = t_spike
                spike_idx += 1

            x_arr += [y0[0]]
            y_arr += [y0[1]]
            z_arr += [y0[2]]

        return x_arr, y_arr, z_arr

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
        x_expected, y_expected, z_expected = self.evaluate_odes_scipy(sigma, rho, beta, inital_state, spike_times, sim_time)

        # NEST simulation
        x = []
        y = []
        z = []
        sim_step_size = 1.
        for i in np.arange(0., sim_time, sim_step_size):
            nest.Simulate(sim_step_size)
            syn_stats = connections.get()  # nest.GetConnections()[2].get()
            x += [syn_stats["x"]]
            y += [syn_stats["y"]]
            z += [syn_stats["z"]]

        #TODO: Adjust tolerance
        np.testing.assert_allclose(x, x_expected, atol=1e-2, rtol=1e-2)
        np.testing.assert_allclose(y, y_expected, atol=1e-2, rtol=1e-2)
        np.testing.assert_allclose(z, z_expected, atol=1e-2, rtol=1e-2)
