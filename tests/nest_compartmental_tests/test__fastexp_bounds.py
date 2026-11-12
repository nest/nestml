# -*- coding: utf-8 -*-
#
# test__fastexp_bounds.py
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
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


DT = 0.1
SIM_TIME = 1.0
GATE_INITIAL = 0.01696863

VARIANTS = {
    "reference": {
        "module_name": "cm_fastexp_bounds_reference_module",
        "suffix": "_fastexp_bounds_reference_nestml",
        "model_name": "cm_default_fastexp_bounds_reference_nestml",
        "codegen_opts": {"use_fastexp": False},
    },
    "fastexp": {
        "module_name": "cm_fastexp_bounds_fastexp_module",
        "suffix": "_fastexp_bounds_fastexp_nestml",
        "model_name": "cm_default_fastexp_bounds_fastexp_nestml",
        "codegen_opts": {"use_fastexp": True},
    },
}


class TestFastExpBounds:
    @pytest.fixture(scope="class", autouse=True)
    def setup_models(self, request):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "cm_default.nestml")

        for variant_name, variant in VARIANTS.items():
            target_path = os.path.join(tests_path, "target", "fastexp_bounds", variant_name)
            install_path = os.path.join(target_path, "install")
            os.makedirs(target_path, exist_ok=True)
            os.makedirs(install_path, exist_ok=True)
            variant["target_path"] = target_path
            variant["module_path"] = os.path.join(install_path, variant["module_name"] + ".so")

            generate_nest_compartmental_target(
                input_path=input_path,
                target_path=target_path,
                install_path=install_path,
                module_name=variant["module_name"],
                suffix=variant["suffix"],
                logging_level="WARNING",
                codegen_opts=variant["codegen_opts"],
            )

        request.cls.VARIANTS = VARIANTS

    def test_inside_bounds_matches_standard_exponential_prediction(self):
        v_comp = -25.0
        reference, fastexp, expected_reference, expected_fastexp = self._run_case(v_comp)

        self._plot_case("inside_bounds", v_comp, reference, fastexp, expected_reference, expected_fastexp)
        np.testing.assert_allclose(reference["m_Na0"], expected_reference, atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(fastexp["m_Na0"], expected_fastexp, atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(fastexp["m_Na0"], reference["m_Na0"], atol=1e-3, rtol=1e-3)

    def test_outside_bounds_matches_clamped_fast_exponential_prediction(self):
        v_comp = 20.0
        reference, fastexp, expected_reference, expected_fastexp = self._run_case(v_comp)

        self._plot_case("outside_bounds", v_comp, reference, fastexp, expected_reference, expected_fastexp)
        np.testing.assert_allclose(reference["m_Na0"], expected_reference, atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(fastexp["m_Na0"], expected_fastexp, atol=1e-12, rtol=1e-12)
        assert np.max(np.abs(fastexp["m_Na0"] - reference["m_Na0"])) > 0.05

    def test_fastexp_gate_variant_uses_fast_propagator_function(self):
        variant = self.VARIANTS["fastexp"]
        source_path = os.path.join(
            variant["target_path"],
            "cm_neuroncurrents_" + variant["model_name"] + ".cpp",
        )

        with open(source_path, "r", encoding="utf-8") as f:
            source = f.read()

        assert "cm_fast_propagator_exp((-__h) / tau_m_Na" in source

    def _run_case(self, v_comp):
        tau_m = self._tau_m_Na(np.asarray([v_comp]))[0]
        reference = self._run_variant("reference", v_comp)
        fastexp = self._run_variant("fastexp", v_comp)
        expected_reference = self._expected_gate_trace(reference["times"], v_comp, np.exp(-DT / tau_m))
        expected_fastexp = self._expected_gate_trace(
            fastexp["times"],
            v_comp,
            self._bounded_fast_propagator(np.asarray([tau_m]))[0],
        )
        return reference, fastexp, expected_reference, expected_fastexp

    def _run_variant(self, variant_name, v_comp):
        variant = self.VARIANTS[variant_name]

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": DT})
        nest.Install(variant["module_path"])

        neuron = nest.Create(variant["model_name"])
        neuron.compartments = [{
            "parent_idx": -1,
            "params": {
                "C_m": 10.0,
                "g_C": 0.0,
                "g_L": 0.0,
                "e_L": 0.0,
                "v_comp": v_comp,
                "m_Na": GATE_INITIAL,
                "h_Na": 1.0,
                "gbar_Na": 1.0,
                "e_Na": v_comp,
                "gbar_K": 0.0,
            },
        }]
        neuron.receptors = [{"comp_idx": 0, "receptor_type": "AMPA"}]
        spike_generator = nest.Create("spike_generator", 1, {"spike_times": [SIM_TIME + 10.0]})
        nest.Connect(
            spike_generator,
            neuron,
            syn_spec={"synapse_model": "static_synapse", "weight": 1.0, "delay": DT, "receptor_type": 0},
        )

        multimeter = nest.Create("multimeter", 1, {"record_from": ["m_Na0"], "interval": DT})
        nest.Connect(multimeter, neuron)
        nest.Simulate(SIM_TIME)
        events = nest.GetStatus(multimeter, "events")[0]

        return {
            "times": np.asarray(events["times"]),
            "m_Na0": np.asarray(events["m_Na0"]),
        }

    def _expected_gate_trace(self, times, v_comp, propagator):
        assert len(times) > 0
        steps = np.rint(times / DT).astype(int)
        gate_inf = self._m_inf_Na(v_comp)
        return gate_inf + (GATE_INITIAL - gate_inf) * np.power(propagator, steps)

    @staticmethod
    def _plot_case(case_name, v_comp, reference, fastexp, expected_reference, expected_fastexp):
        if not TEST_PLOTS:
            return

        fig, axes = plt.subplots(1, 2, figsize=(10, 4), squeeze=False)
        trace_ax = axes[0][0]
        diff_ax = axes[0][1]

        trace_ax.plot(reference["times"], reference["m_Na0"], label="reference")
        trace_ax.plot(fastexp["times"], fastexp["m_Na0"], linestyle="--", label="fastexp")
        trace_ax.plot(reference["times"], expected_reference, linestyle=":", label="reference prediction")
        trace_ax.plot(fastexp["times"], expected_fastexp, linestyle=":", label="fastexp prediction")
        trace_ax.set_title(f"{case_name}: m_Na at v_comp={v_comp:g} mV")
        trace_ax.set_xlabel("time [ms]")
        trace_ax.set_ylabel("m_Na")
        trace_ax.grid(True, alpha=0.3)
        trace_ax.legend(fontsize="x-small")

        diff_ax.plot(reference["times"], np.abs(fastexp["m_Na0"] - reference["m_Na0"]), label="|fastexp - reference|")
        diff_ax.plot(fastexp["times"], np.abs(fastexp["m_Na0"] - expected_fastexp), label="|fastexp - prediction|")
        diff_ax.set_title("absolute differences")
        diff_ax.set_xlabel("time [ms]")
        diff_ax.grid(True, alpha=0.3)
        diff_ax.legend(fontsize="x-small")

        fig.tight_layout()
        output_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            f"fastexp_bounds_{case_name}.png",
        )
        fig.savefig(output_path)
        plt.close(fig)

    @staticmethod
    def _tau_m_Na(v_comp):
        with np.errstate(divide="ignore", invalid="ignore"):
            simd_cse_tmp_Na0 = 0.111111111 * v_comp
            simd_cse_tmp_Na1 = (0.182 * v_comp + 6.372366) / (
                1.0 - 0.0204385321 * np.exp(-simd_cse_tmp_Na0)
            )
            simd_cse_tmp_Na2 = 1.0 / (
                simd_cse_tmp_Na1
                + ((-0.124) * v_comp - 4.341612) / (1.0 - 48.9271929 * np.exp(simd_cse_tmp_Na0))
            )
            return 0.31152648 * simd_cse_tmp_Na2

    @staticmethod
    def _m_inf_Na(v_comp):
        simd_cse_tmp_Na0 = 0.111111111 * v_comp
        simd_cse_tmp_Na1 = (0.182 * v_comp + 6.372366) / (
            1.0 - 0.0204385321 * np.exp(-simd_cse_tmp_Na0)
        )
        simd_cse_tmp_Na2 = 1.0 / (
            simd_cse_tmp_Na1
            + ((-0.124) * v_comp - 4.341612) / (1.0 - 48.9271929 * np.exp(simd_cse_tmp_Na0))
        )
        return simd_cse_tmp_Na1 * simd_cse_tmp_Na2

    @staticmethod
    def _bounded_fast_propagator(tau_values):
        with np.errstate(divide="ignore", invalid="ignore"):
            x = -DT / tau_values
            xc = np.minimum(-1.0e-12, np.maximum(-2.0, x))
            return 0.9999833698215348 + xc * (
                0.9993709968710967 + xc * (
                    0.4961277470116421 + xc * (
                        0.15781341991629894 + xc * (
                            0.03218380466140601 + xc * 0.003214600822495845
                        )
                    )
                )
            )
