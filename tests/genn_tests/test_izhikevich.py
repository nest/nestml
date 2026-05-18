# -*- coding: utf-8 -*-
#
# test_izhikevich.py
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
import pytest

from pynestml.frontend.pynestml_frontend import generate_genn_target

import pygenn
from pygenn import create_neuron_model, create_current_source_model, init_postsynaptic, init_weight_update, GeNNModel


# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestGeNNIzhikevich:
    """
    Tests the code generation and running a little simulation.

    izhikevich_neuron uses convolutions, and uses the forward Euler numeric integrator.
    """

    @pytest.fixture(scope="module", autouse=True)
    def test_genn_izhikevich(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "izhikevich_neuron.nestml"))))
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        suffix = "_nestml"
        module_name = "nestmlmodule"

        generate_genn_target(input_path, target_path,
                             module_name=module_name,
                             logging_level=logging_level,
                             suffix=suffix)

    def test_genn_izhikevich_current_injection(self):
        from nestmlmodule.izhikevich_neuron_nestml import izhikevich_neuron_nestml_model

        # Simulation timestep of model in ms
        TIMESTEP = 1.0
        SIM_TIMESTEPS = 100

        izk_init = {"V_m": -65.0,
                    "U_m": -65.0 * .2}

        izk_params = {"a": 0.02,
                      "b": 0.2,
                      "c": -65.0,
                      "d": 8.0,
                      "V_m_init": -65.0,
                      "V_min": -999,
                      "V_th": 29.99,
                      "I_e": 0.}

        cs_model = create_current_source_model("cs_model",
                                               vars=[("magnitude", "scalar")],
                                               injection_code="injectCurrent(magnitude);")
        model = GeNNModel("float", "tutorial_1")
        model.dt = TIMESTEP
        neuron_pop = model.add_neuron_population("neuron0", 1,
                                                 izhikevich_neuron_nestml_model, izk_params, izk_init)
        neuron_pop.spike_recording_enabled = True
        current_input = model.add_current_source("current_input", cs_model,
                                                 neuron_pop, {}, {"magnitude": 200.0})
        current_input.target_var = "I_stim"
        model.build()
        model.load(num_recording_timesteps=SIM_TIMESTEPS)

        V_m_log = []
        while model.timestep < SIM_TIMESTEPS:
            model.step_time()
            neuron_pop.vars["V_m"].pull_from_device()
            V_m_log.append(neuron_pop.vars["V_m"].values)

        model.pull_recording_buffers_from_device()

        spike_times, spike_ids = neuron_pop.spike_recording_data[0]

        if TEST_PLOTS:
            fig, ax = plt.subplots()

            ax.scatter(spike_times, spike_ids, s=1)
            ax.set_ylabel("Neuron ID")
            ax.set_xlim((0, SIM_TIMESTEPS * TIMESTEP))

            fig.savefig("/tmp/genn_izhikevich_current_injection.png")
            plt.close(fig)

        assert len(spike_times) > 52

    def test_genn_izhikevich_postsynaptic_response(self):
        from nestmlmodule.izhikevich_neuron_nestml import izhikevich_neuron_nestml_model

        # Simulation timestep of model in ms
        TIMESTEP = 1.0
        SIM_TIMESTEPS = 100

        izk_init = {"V_m": -65.0,
                    "U_m": -65.0 * .2}

        izk_params = {"a": 0.02,
                      "b": 0.2,
                      "c": -65.0,
                      "d": 8.0,
                      "V_m_init": -65.0,
                      "V_min": -999,
                      "V_th": 29.99,
                      "I_e": 0.}

        model = GeNNModel("float", "tutorial_1")
        model.dt = TIMESTEP
        neuron_pop = model.add_neuron_population("neuron0", 1,
                                                 izhikevich_neuron_nestml_model, izk_params, izk_init)
        neuron_pop.spike_recording_enabled = True

        poisson_gen_pop = model.add_neuron_population("my_poisson_gen", 1,
                                                      "Poisson", {"rate": 200.}, {"timeStepToSpike": 1})
        poisson_gen_pop.spike_recording_enabled = True
        syn_pop = model.add_synapse_population("synapse_0_1", "DENSE",
                                               poisson_gen_pop, neuron_pop,
                                               init_weight_update("StaticPulse", {}, {"g": 100.}),
                                               init_postsynaptic("DeltaCurr"))
        syn_pop.post_target_var = "spikes"

        model.build()
        model.load(num_recording_timesteps=SIM_TIMESTEPS)

        V_m_log = []
        while model.timestep < SIM_TIMESTEPS:
            model.step_time()
            neuron_pop.vars["V_m"].pull_from_device()
            V_m_log.append(neuron_pop.vars["V_m"].values)

        model.pull_recording_buffers_from_device()

        spike_times, spike_ids = neuron_pop.spike_recording_data[0]

        if TEST_PLOTS:
            fig, ax = plt.subplots(figsize=(5, 1.5))

            ax.scatter(spike_times, spike_ids, s=1)
            ax.set_ylabel("Neuron ID")
            ax.set_xlim((0, SIM_TIMESTEPS * TIMESTEP))
            fig.tight_layout()

            fig.savefig("/tmp/genn_izhikevich_postsynaptic_response.png", dpi=300)
            plt.close(fig)

        assert len(spike_times) > 10
