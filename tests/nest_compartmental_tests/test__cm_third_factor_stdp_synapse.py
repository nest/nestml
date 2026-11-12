# -*- coding: utf-8 -*-
#
# test__cm_third_factor_stdp_synapse.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


DT = 0.1
MODULE_NAME = "cm_third_factor_stdp_module"
MODEL_NAME = "multichannel_test_model_nestml"
RECEPTOR_TYPE = "AMPA_third_factor_stdp_synapse_nestml"
SIM_TIME = 35.0
POST_SPIKE_TIME = 15.0
INITIAL_WEIGHT = 10.0


class TestCmThirdFactorStdpSynapse:
    @pytest.fixture(scope="class", autouse=True)
    def setup_model(self, request):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        resources_path = os.path.join(tests_path, "resources")
        target_path = os.path.join(tests_path, "target", "cm_third_factor_stdp_synapse")
        install_path = os.path.join(target_path, "install")
        os.makedirs(target_path, exist_ok=True)
        os.makedirs(install_path, exist_ok=True)

        generate_nest_compartmental_target(
            input_path=[
                os.path.join(resources_path, "concmech.nestml"),
                os.path.join(resources_path, "cm_third_factor_stdp_synapse.nestml"),
            ],
            target_path=target_path,
            install_path=install_path,
            module_name=MODULE_NAME,
            suffix="_nestml",
            logging_level="WARNING",
            codegen_opts={
                "neuron_synapse_pairs": [{
                    "neuron": "multichannel_test_model",
                    "synapses": {
                        "third_factor_stdp_synapse": {"post_ports": ["post_spikes"]},
                    },
                }],
                "weight_variable": {"third_factor_stdp_synapse": "w"},
            },
        )

        request.cls.module_path = os.path.join(install_path, MODULE_NAME + ".so")

    def test_third_factor_modulates_weight_updates(self):
        blocked = self._run_case(third_factor_scale=0.0)
        active = self._run_case(third_factor_scale=1.0)

        assert np.allclose(blocked["I_post_dend"], 0.0, atol=1e-12)
        assert np.max(active["I_post_dend"]) > 1.0
        assert blocked["post_spikes"].size == 1
        assert active["post_spikes"].size == 1

        blocked_weight_change = abs(blocked["weight"][-1] - blocked["weight"][0])
        active_weight_change = abs(active["weight"][-1] - active["weight"][0])

        self._plot_results(blocked, active)
        self._print_weight_differences(blocked, active)

        assert blocked_weight_change < 1e-6
        assert active_weight_change > 1e-4
        assert active["weight"][-1] > blocked["weight"][-1]

    def _run_case(self, third_factor_scale):
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": DT})
        nest.Install(self.module_path)

        pre_spike_times = [10.0]
        external_input_pre = nest.Create("spike_generator", params={"spike_times": pre_spike_times})
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(MODEL_NAME)

        post_neuron.compartments = [{
            "parent_idx": -1,
            "params": {
                "C_m": 10.0,
                "g_C": 0.0,
                "g_L": 1.5,
                "e_L": -70.0,
                "v_comp": -70.0,
                "gbar_Ca_HVA": 0.0,
                "gbar_Ca_LVAst": 0.0,
                "gbar_NaTa_t": 0.0,
                "gbar_SKv3_1": 0.0,
                "gbar_SK_E2": 0.0,
            },
        }]
        post_neuron.receptors = [
            {
                "comp_idx": 0,
                "receptor_type": RECEPTOR_TYPE,
                "params": {
                    "w": INITIAL_WEIGHT,
                    "d": DT,
                    "e_AMPA": -70.0,
                    "third_factor_scale": third_factor_scale,
                },
            },
            {
                "comp_idx": 0,
                "receptor_type": "AMPA",
                "params": {
                    "e_AMPA": 0.0,
                },
            },
        ]

        nest.Connect(
            external_input_pre,
            pre_neuron,
            "one_to_one",
            syn_spec={"synapse_model": "static_synapse", "weight": 2.0, "delay": DT},
        )
        nest.Connect(
            pre_neuron,
            post_neuron,
            "one_to_one",
            syn_spec={"synapse_model": "static_synapse", "weight": 0.001, "delay": DT, "receptor_type": 0},
        )
        nest.Connect(
            pre_neuron,
            post_neuron,
            "one_to_one",
            syn_spec={"synapse_model": "static_synapse", "weight": 1.0, "delay": DT, "receptor_type": 1},
        )

        recordables = [
            "v_comp0",
            "w0",
            "pre_trace0",
            "post_trace0",
            "I_post_dend0",
            RECEPTOR_TYPE + "0",
        ]
        multimeter = nest.Create("multimeter", 1, {"record_from": recordables, "interval": DT})
        pre_spike_recorder = nest.Create("spike_recorder")
        post_spike_recorder = nest.Create("spike_recorder")

        nest.Connect(multimeter, post_neuron)
        nest.Connect(pre_neuron, pre_spike_recorder)
        nest.Connect(post_neuron, post_spike_recorder)

        nest.Simulate(POST_SPIKE_TIME)
        nest.SetStatus(post_neuron, {"v_comp0": 0.0})
        nest.Simulate(SIM_TIME - POST_SPIKE_TIME)

        events = nest.GetStatus(multimeter, "events")[0]
        return {
            "times": np.asarray(events["times"]),
            "v_comp": np.asarray(events["v_comp0"]),
            "weight": np.asarray(events["w0"]),
            "pre_trace": np.asarray(events["pre_trace0"]),
            "post_trace": np.asarray(events["post_trace0"]),
            "I_post_dend": np.asarray(events["I_post_dend0"]),
            "receptor_current": np.asarray(events[RECEPTOR_TYPE + "0"]),
            "pre_spikes": np.asarray(nest.GetStatus(pre_spike_recorder, "events")[0]["times"]),
            "post_spikes": np.asarray(nest.GetStatus(post_spike_recorder, "events")[0]["times"]),
        }

    def _plot_results(self, blocked, active):
        if not TEST_PLOTS:
            return

        tests_path = os.path.realpath(os.path.dirname(__file__))
        output_path = os.path.join(tests_path, "cm_third_factor_stdp_synapse.png")

        fig, axs = plt.subplots(3, 2, figsize=(12, 9), sharex=True)
        axs = axs.flatten()

        self._plot_trace_pair(axs[0], blocked, active, "weight", "weight")
        self._plot_trace_pair(axs[1], blocked, active, "I_post_dend", "third factor current")
        self._plot_trace_pair(axs[2], blocked, active, "pre_trace", "pre trace")
        self._plot_trace_pair(axs[3], blocked, active, "post_trace", "post trace")
        self._plot_trace_pair(axs[4], blocked, active, "receptor_current", "third-factor synapse current")
        self._plot_trace_pair(axs[5], blocked, active, "v_comp", "v_comp")

        for ax in axs:
            for spike_time in blocked["pre_spikes"]:
                ax.axvline(spike_time, color="black", linestyle=":", linewidth=0.8)
            for spike_time in active["post_spikes"]:
                ax.axvline(spike_time, color="red", linestyle=":", linewidth=0.8)
            ax.legend(loc="best")

        axs[-1].set_xlabel("time [ms]")
        axs[-2].set_xlabel("time [ms]")
        fig.tight_layout()
        fig.savefig(output_path, dpi=200)
        plt.close(fig)

    @staticmethod
    def _plot_trace_pair(ax, blocked, active, variable_name, title):
        ax.plot(blocked["times"], blocked[variable_name], label="third factor blocked")
        ax.plot(active["times"], active[variable_name], linestyle="--", label="third factor active")
        ax.set_title(title)

    @staticmethod
    def _print_weight_differences(blocked, active):
        blocked_change = blocked["weight"][-1] - blocked["weight"][0]
        active_change = active["weight"][-1] - active["weight"][0]
        final_difference = active["weight"][-1] - blocked["weight"][-1]

        print("Third-factor STDP weight differences:")
        print(
            f"  blocked: initial={blocked['weight'][0]:.12g}, "
            f"final={blocked['weight'][-1]:.12g}, diff={blocked_change:.12g}"
        )
        print(
            f"  active: initial={active['weight'][0]:.12g}, "
            f"final={active['weight'][-1]:.12g}, diff={active_change:.12g}"
        )
        print(f"  active final - blocked final: {final_difference:.12g}")
