# -*- coding: utf-8 -*-
#
# nest_integration_test.py
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
import pytest
import re

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


def get_model_doc_title(model_fname: str):
    with open(model_fname) as f:
        model = f.read()
        return re.compile(r'\"\"\"[^#]*###').search(model).group()[3:-3].strip()


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNestIntegration:

    def generate_all_models(self):
        codegen_opts = {}

        if NESTTools.detect_nest_version().startswith("v3"):
            codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
            codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"

        generate_nest_target(input_path=["models/neurons/hh_cond_exp_traub_neuron.nestml",
                                         "models/neurons/hh_psc_alpha_neuron.nestml",
                                         "models/neurons/iaf_cond_beta_neuron.nestml",
                                         "models/neurons/iaf_cond_alpha_neuron.nestml",
                                         "models/neurons/iaf_cond_exp_neuron.nestml",
                                         "models/neurons/iaf_psc_alpha_neuron.nestml",
                                         "models/neurons/iaf_psc_exp_neuron.nestml",
                                         "models/neurons/iaf_psc_delta_neuron.nestml"],
                             target_path="/tmp/nestml-allmodels",
                             logging_level="DEBUG",
                             module_name="nestml_allmodels_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

        # generate code with analytic solver disabled
        alt_codegen_opts = {**codegen_opts, **{"solver": "numeric"}}

        generate_nest_target(input_path=["models/neurons/aeif_cond_exp_neuron.nestml",
                                         "models/neurons/aeif_cond_alpha_neuron.nestml"],
                             target_path="/tmp/nestml-alt-allmodels",
                             logging_level="DEBUG",
                             module_name="nestml_alt_allmodels_module",
                             suffix="_alt_nestml",
                             codegen_opts=alt_codegen_opts)

        # generate code using forward Euler integrator
        alt_codegen_opts = {**codegen_opts, **{"numeric_solver": "forward-Euler"}}

        generate_nest_target(input_path="models/neurons/izhikevich_neuron.nestml",
                             target_path="/tmp/nestml-alt-int-allmodels",
                             logging_level="DEBUG",
                             module_name="nestml_alt_int_allmodels_module",
                             suffix="_alt_int_nestml",
                             codegen_opts=alt_codegen_opts)

    def test_nest_integration(self):
        self.generate_all_models()
        nest.Install("nestml_allmodels_module")
        nest.Install("nestml_alt_allmodels_module")
        nest.Install("nestml_alt_int_allmodels_module")

        self._test_model_equivalence_subthreshold("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")
        self._test_model_equivalence_fI_curve("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")
        self._test_model_equivalence_fI_curve("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")
        self._test_model_equivalence_fI_curve("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_cond_exp", "iaf_cond_exp_neuron_nestml", tolerance=1E-6)  # large tolerance because NESTML integrates PSCs precisely whereas NEST uses GSL
        self._test_model_equivalence_spiking("iaf_cond_exp", "iaf_cond_exp_neuron_nestml", tolerance=1E-6)  # large tolerance because NESTML integrates PSCs precisely whereas NEST uses GSL
        self._test_model_equivalence_fI_curve("iaf_cond_exp", "iaf_cond_exp_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_cond_exp", "iaf_cond_exp_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")
        self._test_model_equivalence_fI_curve("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")

        iaf_cond_beta_nest_model_parameters = {"tau_rise_ex": 2., "tau_decay_ex": 10.}
        iaf_cond_beta_nestml_model_parameters = {"tau_syn_rise_E": 2., "tau_syn_decay_E": 10.}    # XXX: TODO: does not work yet when tau_rise = tau_fall (numerical singularity occurs in the propagators)
        self._test_model_equivalence_subthreshold("iaf_cond_beta", "iaf_cond_beta_neuron_nestml", nest_model_parameters=iaf_cond_beta_nest_model_parameters, nestml_model_parameters=iaf_cond_beta_nestml_model_parameters)
        self._test_model_equivalence_spiking("iaf_cond_beta", "iaf_cond_beta_neuron_nestml", nest_model_parameters=iaf_cond_beta_nest_model_parameters, nestml_model_parameters=iaf_cond_beta_nestml_model_parameters)
        self._test_model_equivalence_fI_curve("iaf_cond_beta", "iaf_cond_beta_neuron_nestml")

        self._test_model_equivalence_subthreshold("izhikevich", "izhikevich_neuron_alt_int_nestml")
        self._test_model_equivalence_spiking("izhikevich", "izhikevich_neuron_alt_int_nestml")
        self._test_model_equivalence_fI_curve("izhikevich", "izhikevich_neuron_alt_int_nestml")

        nestml_hh_psc_alpha_model_parameters = {"gsl_abs_error_tol": 1E-3, "gsl_rel_error_tol": 0.}  # matching the defaults in NEST
        self._test_model_equivalence_subthreshold("hh_psc_alpha", "hh_psc_alpha_neuron_nestml", nestml_model_parameters=nestml_hh_psc_alpha_model_parameters)
        self._test_model_equivalence_spiking("hh_psc_alpha", "hh_psc_alpha_neuron_nestml", tolerance=1E-5, nestml_model_parameters=nestml_hh_psc_alpha_model_parameters)
        self._test_model_equivalence_fI_curve("hh_psc_alpha", "hh_psc_alpha_neuron_nestml", nestml_model_parameters=nestml_hh_psc_alpha_model_parameters)

        nestml_hh_cond_exp_traub_model_parameters = {"gsl_abs_error_tol": 1E-3, "gsl_rel_error_tol": 0.}  # matching the defaults in NEST
        self._test_model_equivalence_subthreshold("hh_cond_exp_traub", "hh_cond_exp_traub_neuron_nestml", nestml_model_parameters=nestml_hh_cond_exp_traub_model_parameters)
        self._test_model_equivalence_fI_curve("hh_cond_exp_traub", "hh_cond_exp_traub_neuron_nestml", nestml_model_parameters=nestml_hh_cond_exp_traub_model_parameters)

        self._test_model_equivalence_subthreshold("aeif_cond_exp", "aeif_cond_exp_neuron_alt_nestml", kernel_opts={"resolution": .01})    # needs resolution 0.01 because the NEST model overrides this internally. Subthreshold only because threshold detection is inside the while...gsl_odeiv_evolve_apply() loop in NEST but outside the loop (strictly after gsl_odeiv_evolve_apply()) in NESTML, causing spike times to differ slightly
        self._test_model_equivalence_fI_curve("aeif_cond_exp", "aeif_cond_exp_neuron_alt_nestml")

        self._test_model_equivalence_subthreshold("aeif_cond_alpha", "aeif_cond_alpha_neuron_alt_nestml", kernel_opts={"resolution": .01})    # needs resolution 0.01 because the NEST model overrides this internally. Subthreshold only because threshold detection is inside the while...gsl_odeiv_evolve_apply() loop in NEST but outside the loop (strictly after gsl_odeiv_evolve_apply()) in NESTML, causing spike times to differ slightly
        self._test_model_equivalence_fI_curve("aeif_cond_alpha", "aeif_cond_alpha_neuron_alt_nestml")

        # --------------
        # XXX: TODO!

        # self._test_model_equivalence_subthreshold("ht_neuron", "hill_tononi_neuron_nestml", syn_spec={"receptor_type": 1})
        # self._test_model_equivalence_spiking("ht_neuron", "hill_tononi_neuron_nestml", tolerance=1E-3, syn_spec={"receptor_type": 1})
        # self._test_model_equivalence_fI_curve("ht_neuron", "hill_tononi_neuron_nestml", syn_spec={"receptor_type": 1})

        # neuron_models.append(("iaf_chxk_2008", "iaf_chxk_2008_nestml", 10., default_tolerance))   # TODO because NESTML does not support SpikeEvent.set_offset()
        # models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_nestml", 1.e-3, 1E-3))
        # models.append(("iaf_tum_2000", "iaf_tum_2000_nestml", None, 0.01))
        # models.append(("mat2_psc_exp", "mat2_psc_exp_nestml", None, 0.1))

    def _test_model_equivalence_subthreshold(self, nest_model_name, nestml_model_name, gsl_error_tol=1E-3, tolerance=1E-7, tolerance_spiketimes=1E-9, nest_model_parameters=None, nestml_model_parameters=None, model_initial_state=None, kernel_opts=None, syn_spec=None):
        self._test_model_equivalence_psc(nest_model_name, nestml_model_name, gsl_error_tol, tolerance, tolerance_spiketimes, nest_model_parameters, nestml_model_parameters, model_initial_state, kernel_opts=kernel_opts, fname_snip="[subthreshold]_", syn_spec=syn_spec)

    def _test_model_equivalence_spiking(self, nest_model_name, nestml_model_name, gsl_error_tol=1E-3, tolerance=1E-7, tolerance_spiketimes=1E-9, nest_model_parameters=None, nestml_model_parameters=None, model_initial_state=None, kernel_opts=None, syn_spec=None):
        self._test_model_equivalence_psc(nest_model_name, nestml_model_name, gsl_error_tol, tolerance, tolerance_spiketimes, nest_model_parameters, nestml_model_parameters, model_initial_state, max_weight=5000., kernel_opts=kernel_opts, fname_snip="[spiking]_", syn_spec=syn_spec)

    def _test_model_equivalence_curr_inj(self, nest_model_name, nestml_model_name, gsl_error_tol=1E-3, tolerance=1E-7, nest_model_parameters=None, nestml_model_parameters=None, model_initial_state=None, kernel_opts=None, t_stop=1000., t_pulse_start=100., t_pulse_stop=300.):
        """For different levels of injected current, verify that behaviour is the same between NEST and NESTML"""

        I_stim_vec = np.linspace(10E-12, 1E-9, 3)  # [A]
        for i, I_stim in enumerate(I_stim_vec):
            nest.ResetKernel()
            if kernel_opts:
                nest.SetKernelStatus(kernel_opts)

            try:
                nest.Install("nestml_allmodels_module")
                nest.Install("nestml_alt_allmodels_module")
                nest.Install("nestml_alt_int_allmodels_module")
            except Exception:
                # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
                pass

            neuron1 = nest.Create(nest_model_name, params=nest_model_parameters)
            neuron2 = nest.Create(nestml_model_name, params=nestml_model_parameters)
            if model_initial_state is not None:
                nest.SetStatus(neuron1, model_initial_state)
                nest.SetStatus(neuron2, model_initial_state)

            # if gsl_error_tol is not None:
            #     nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

            dc = nest.Create("dc_generator", params={"amplitude": 0.})

            nest.Connect(dc, neuron1)
            nest.Connect(dc, neuron2)

            multimeter1 = nest.Create("multimeter")
            multimeter2 = nest.Create("multimeter")

            V_m_specifier = "V_m"  # "delta_V_m"
            nest.SetStatus(multimeter1, {"record_from": [V_m_specifier]})
            nest.SetStatus(multimeter2, {"record_from": [V_m_specifier]})

            nest.Connect(multimeter1, neuron1)
            nest.Connect(multimeter2, neuron2)

            if NESTTools.detect_nest_version().startswith("v2"):
                sd_reference = nest.Create("spike_detector")
                sd_testant = nest.Create("spike_detector")
            else:
                sd_reference = nest.Create("spike_recorder")
                sd_testant = nest.Create("spike_recorder")

            nest.Connect(neuron1, sd_reference)
            nest.Connect(neuron2, sd_testant)

            nest.Simulate(t_pulse_start)
            dc.amplitude = I_stim * 1E12  # 1E12: convert A to pA
            nest.Simulate(t_pulse_stop - t_pulse_start)
            dc.amplitude = 0.
            nest.Simulate(t_stop - t_pulse_stop)

            dmm1 = nest.GetStatus(multimeter1)[0]
            Vms1 = dmm1["events"][V_m_specifier]
            ts1 = dmm1["events"]["times"]

            dmm2 = nest.GetStatus(multimeter2)[0]
            Vms2 = dmm2["events"][V_m_specifier]
            ts2 = dmm2["events"]["times"]

            if TEST_PLOTS:
                fig, ax = plt.subplots(3, 1)
                ax[0].plot(ts1, Vms1, label="Reference " + nest_model_name)
                ax[0].plot(ts2, Vms2, label="Testant " + nestml_model_name)
                ax[1].plot([0, t_pulse_start, t_pulse_start, t_pulse_stop, t_pulse_stop, t_stop], [0, 0, I_stim, I_stim, 0, 0], label="I_inj")
                ax[2].semilogy(ts1, np.abs(Vms1 - Vms2), label="error")
                for _ax in ax:
                    _ax.legend(loc="upper right")
                    _ax.grid()
                plt.savefig("/tmp/nestml_nest_integration_test_pulse_[" + nest_model_name + "]_[" + nestml_model_name + "]_[I_stim=" + str(I_stim) + "].png")
                plt.close(fig)

            np.testing.assert_allclose(Vms1, Vms2)

    def _test_model_equivalence_fI_curve(self, nest_model_name, nestml_model_name, gsl_error_tol=1E-3, tolerance=1E-7, nest_model_parameters=None, nestml_model_parameters=None, model_initial_state=None, kernel_opts=None):
        """For different levels of injected current, verify that behaviour is the same between NEST and NESTML"""
        t_stop = 1000.  # [ms]

        I_stim_vec = np.linspace(10E-12, 1E-9, 3)  # [A]
        rate_testant = float("nan") * np.ones_like(I_stim_vec)
        rate_reference = float("nan") * np.ones_like(I_stim_vec)
        for i, I_stim in enumerate(I_stim_vec):

            nest.ResetKernel()
            if kernel_opts:
                nest.SetKernelStatus(kernel_opts)

            try:
                nest.Install("nestml_allmodels_module")
                nest.Install("nestml_alt_allmodels_module")
                nest.Install("nestml_alt_int_allmodels_module")
            except Exception:
                # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
                pass

            neuron1 = nest.Create(nest_model_name, params=nest_model_parameters)
            neuron2 = nest.Create(nestml_model_name, params=nestml_model_parameters)
            if model_initial_state is not None:
                nest.SetStatus(neuron1, model_initial_state)
                nest.SetStatus(neuron2, model_initial_state)

            # if gsl_error_tol is not None:
            #     nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

            dc = nest.Create("dc_generator", params={"amplitude": 1E12 * I_stim})  # 1E12: convert A to pA

            nest.Connect(dc, neuron1)
            nest.Connect(dc, neuron2)

            multimeter1 = nest.Create("multimeter")
            multimeter2 = nest.Create("multimeter")

            V_m_specifier = "V_m"  # "delta_V_m"
            nest.SetStatus(multimeter1, {"record_from": [V_m_specifier]})
            nest.SetStatus(multimeter2, {"record_from": [V_m_specifier]})

            nest.Connect(multimeter1, neuron1)
            nest.Connect(multimeter2, neuron2)

            if NESTTools.detect_nest_version().startswith("v2"):
                sd_reference = nest.Create("spike_detector")
                sd_testant = nest.Create("spike_detector")
            else:
                sd_reference = nest.Create("spike_recorder")
                sd_testant = nest.Create("spike_recorder")

            nest.Connect(neuron1, sd_reference)
            nest.Connect(neuron2, sd_testant)

            nest.Simulate(t_stop)

            dmm1 = nest.GetStatus(multimeter1)[0]
            Vms1 = dmm1["events"][V_m_specifier]
            ts1 = dmm1["events"]["times"]

            dmm2 = nest.GetStatus(multimeter2)[0]
            Vms2 = dmm2["events"][V_m_specifier]
            ts2 = dmm2["events"]["times"]

            rate_testant[i] = nest.GetStatus(sd_testant)[0]["n_events"] / t_stop * 1000
            rate_reference[i] = nest.GetStatus(sd_reference)[0]["n_events"] / t_stop * 1000

            if TEST_PLOTS:
                fig, ax = plt.subplots(2, 1)
                ax[0].plot(ts1, Vms1, label="Reference " + nest_model_name)
                ax[1].plot(ts2, Vms2, label="Testant " + nestml_model_name)
                for _ax in ax:
                    _ax.legend(loc="upper right")
                    _ax.grid()
                fig.suptitle("Rate: " + str(rate_testant[i]) + " Hz")
                plt.savefig("/tmp/nestml_nest_integration_test_subthreshold_[" + nest_model_name + "]_[" + nestml_model_name + "]_[I_stim=" + str(I_stim) + "].png")
                plt.close(fig)

        if TEST_PLOTS:
            if len(I_stim_vec) < 20:
                marker = "o"
            else:
                marker = None
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(I_stim_vec * 1E12, rate_reference, marker=marker, label="Reference " + nest_model_name)
            ax[1].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label="Testant " + nestml_model_name)
            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.grid()
                _ax.set_ylabel("Firing rate [Hz]")
            ax[1].set_xlabel("$I_{inj}$ [pA]")
            plt.savefig("/tmp/nestml_nest_integration_test_subthreshold_[" + nest_model_name + "]_[" + nestml_model_name + "].png")
            plt.close(fig)

            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label=nest_model_name)
                for _ax in ax:
                    _ax.grid()
                    _ax.set_ylabel("Firing rate [Hz]")
                ax[0].set_xlabel("$I_{inj}$ [pA]")
                plt.tight_layout()
                plt.savefig("/tmp/nestml_models_library_[" + nest_model_name + "]_f-I_curve" + fname_snip + ".png")
                plt.close(fig)

    def _test_model_equivalence_psc(self, nest_model_name, nestml_model_name, gsl_error_tol, tolerance=None, tolerance_spiketimes=1E-9, nest_model_parameters=None, nestml_model_parameters=None, model_initial_state=None, max_weight: float = 10., compare_V_m_traces: bool = True, kernel_opts=None, fname_snip="", syn_spec=None):

        spike_times = np.linspace(100, 200, 11)
        spike_weights = np.linspace(1, max_weight, 11)

        nest.ResetKernel()
        if kernel_opts:
            nest.SetKernelStatus(kernel_opts)

        try:
            nest.Install("nestml_allmodels_module")
            nest.Install("nestml_alt_allmodels_module")
            nest.Install("nestml_alt_int_allmodels_module")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        neuron1 = nest.Create(nest_model_name, params=nest_model_parameters)
        neuron2 = nest.Create(nestml_model_name, params=nestml_model_parameters)

        if model_initial_state is not None:
            nest.SetStatus(neuron1, model_initial_state)
            nest.SetStatus(neuron2, model_initial_state)

        # if gsl_error_tol is not None:
        #     nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

        spikegenerator = nest.Create("spike_generator",
                                     params={"spike_times": spike_times, "spike_weights": spike_weights})

        nest.Connect(spikegenerator, neuron1, syn_spec=syn_spec)
        nest.Connect(spikegenerator, neuron2, syn_spec=syn_spec)

        spike_recorder1 = nest.Create("spike_recorder")
        spike_recorder2 = nest.Create("spike_recorder")
        nest.Connect(neuron1, spike_recorder1)
        nest.Connect(neuron2, spike_recorder2)

        multimeter1 = nest.Create("multimeter")
        multimeter2 = nest.Create("multimeter")

        V_m_specifier = "V_m"
        nest.SetStatus(multimeter1, {"record_from": [V_m_specifier]})
        nest.SetStatus(multimeter2, {"record_from": [V_m_specifier]})

        nest.Connect(multimeter1, neuron1)
        nest.Connect(multimeter2, neuron2)

        nest.Simulate(400.)

        dmm1 = nest.GetStatus(multimeter1)[0]
        Vms1 = dmm1["events"][V_m_specifier]
        ts1 = dmm1["events"]["times"]

        dmm2 = nest.GetStatus(multimeter2)[0]
        Vms2 = dmm2["events"][V_m_specifier]
        ts2 = dmm2["events"]["times"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(3, 1)
            ax[0].plot(ts1, Vms1, label="Reference " + nest_model_name)
            ax[0].scatter(spike_recorder1.events["times"], Vms1[0] * np.ones_like(spike_recorder1.events["times"]))
            ax[1].plot(ts2, Vms2, label="Testant " + nestml_model_name)
            ax[1].scatter(spike_recorder2.events["times"], Vms2[0] * np.ones_like(spike_recorder2.events["times"]))
            ax[2].semilogy(ts2, np.abs(Vms1 - Vms2), label="Error", color="red")
            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_integration_test_psc_[" + nest_model_name + "]_[" + nestml_model_name + "].png")
            plt.close(fig)

        np.testing.assert_allclose(ts1, ts2)

        if compare_V_m_traces:
            # check that V_m timeseries match
            np.testing.assert_allclose(Vms1, Vms2, rtol=tolerance)

        # check that spike times match (if any)
        np.testing.assert_allclose(spike_recorder1.events["times"], spike_recorder2.events["times"], rtol=tolerance_spiketimes)
