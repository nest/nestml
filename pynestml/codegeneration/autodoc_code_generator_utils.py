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

import re

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.string_utils import removeprefix, removesuffix

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


class AutoDocCodeGeneratorUtils:

    def generate_all_models(self):
        codegen_opts = {}
        if NESTTools.detect_nest_version().startswith("v3"):
            codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
            codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"
        codegen_opts={}

        generate_nest_target(input_path=["models/neurons"],
                             target_path="/tmp/nestml-autodoc",
                             logging_level="DEBUG",
                             module_name="nestml_autodoc_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    def test_nest_integration(self):
        default_tolerance = 1E-7   # default relative tolerance when comparing NEST and NESTML results via np.testing.assert_allclose()

        # N.B. all models are assumed to have been already built in the continuous integration script
        self.generate_all_models()

        nest.ResetKernel()

        try:
            nest.Install("nestml_autodoc_module")
        except Exception:
            self.generate_all_models()
            nest.Install("nestml_autodoc_module")

        s = "Models library\n==============\n\n"

        s += "Neuron models\n~~~~~~~~~~~~~\n\n"

        neuron_models = []

        self._test_model_equivalence_subthreshold("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_delta", "iaf_psc_delta_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_exp", "iaf_psc_exp_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_psc_alpha", "iaf_psc_alpha_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_cond_exp", "iaf_cond_exp_neuron_nestml", tol=1E-6)  # large tolerance because NESTML integrates PSCs precisely whereas NEST uses GSL
        self._test_model_equivalence_spiking("iaf_cond_exp", "iaf_cond_exp_neuron_nestml", tol=1E-6)  # large tolerance because NESTML integrates PSCs precisely whereas NEST uses GSL
        self._test_model_equivalence_curr_inj("iaf_cond_exp", "iaf_cond_exp_neuron_nestml")

        self._test_model_equivalence_subthreshold("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")
        self._test_model_equivalence_spiking("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")
        self._test_model_equivalence_curr_inj("iaf_cond_alpha", "iaf_cond_alpha_neuron_nestml")

        iaf_cond_beta_nest_model_parameters = {"tau_rise_ex": 2., "tau_decay_ex": 10.}
        iaf_cond_beta_nestml_model_parameters = {"tau_syn_rise_E": 2., "tau_syn_decay_E": 10.}    # XXX: TODO: does not work yet when tau_rise = tau_fall (numerical singularity occurs in the propagators)
        self._test_model_equivalence_subthreshold("iaf_cond_beta", "iaf_cond_beta_neuron_nestml", nest_model_parameters=iaf_cond_beta_nest_model_parameters, nestml_model_parameters=iaf_cond_beta_nestml_model_parameters)
        self._test_model_equivalence_spiking("iaf_cond_beta", "iaf_cond_beta_neuron_nestml", nest_model_parameters=iaf_cond_beta_nest_model_parameters, nestml_model_parameters=iaf_cond_beta_nestml_model_parameters)
        self._test_model_equivalence_curr_inj("iaf_cond_beta", "iaf_cond_beta_neuron_nestml")

        # XXX: TODO should be fixed after merging fix for ternary operators
        # self._test_model_equivalence_subthreshold("ht_neuron", "hill_tononi_nestml")
        # self._test_model_equivalence_spiking("ht_neuron", "hill_tononi_nestml", tol=1E-3)
        # self._test_model_equivalence_curr_inj("ht_neuron", "hill_tononi_nestml")

        # # XXX: cannot test Izhikevich model due to different integration order. See https://github.com/nest/nest-simulator/issues/2647
        # # if NESTTools.detect_nest_version().startswith("v2"):
        # #     neuron_models.append(("izhikevich", "izhikevich_nestml", None, 1E-6, {}, {}, {"V_m": -70., "U_m": .2 * -70.}))        # large tolerance because NEST Simulator model does not use GSL solver, but simple forward Euler
        # # else:
        # neuron_models.append(("izhikevich", "izhikevich_nestml", None, 1E-6))        # large tolerance because NEST Simulator model does not use GSL solver, but simple forward Euler

        self._test_model_equivalence_subthreshold("hh_psc_alpha", "hh_psc_alpha_neuron_nestml")
        self._test_model_equivalence_spiking("hh_psc_alpha", "hh_psc_alpha_neuron_nestml")
        self._test_model_equivalence_curr_inj("hh_psc_alpha", "hh_psc_alpha_neuron_nestml")        # hh_psc_alpha_model_parameters = {"I_e": 100.}

        neuron_models.append(("aeif_cond_exp", "aeif_cond_exp_alt_nestml", None, default_tolerance, None, None, None,["test_subthreshold_only"])) # needs resolution 0.01 because the NEST model overrides this internally. Subthreshold because threshold detection is inside the while...gsl_odeiv_evolve_apply() loop in NEST but outside the loop (strictly after gsl_odeiv_evolve_apply()) in NESTML, causing spike times to differ slightly
        # neuron_models.append(("aeif_cond_alpha", "aeif_cond_alpha_nestml", None, default_tolerance))"""
        # neuron_models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_nestml", None, 1E-6))   # larger tolerance because NESTML solves PSCs analytically; NEST solves all ODEs numerically

        # --------------
        # XXX: TODO!

        # neuron_models.append(("iaf_chxk_2008", "iaf_chxk_2008_nestml", 10., default_tolerance))   # TODO because NESTML does not support SpikeEvent.set_offset()
        # models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_nestml", 1.e-3, 1E-3))
        # models.append(("iaf_tum_2000", "iaf_tum_2000_nestml", None, 0.01))
        # models.append(("mat2_psc_exp", "mat2_psc_exp_nestml", None, 0.1))

    def _test_model_equivalence_subthreshold(self, nest_model_name, nestml_model_name,
        self._test_model_psc(nest_model_name, nestml_model_name, gsl_error_tol, tolerance, nest_ref_model_opts, custom_model_opts, model_initial_state)

    def _test_model_equivalence_subthreshold(self, nest_model_name, nestml_model_name,
        self._test_model_psc(nest_model_name, nestml_model_name, gsl_error_tol, tolerance, nest_ref_model_opts, custom_model_opts, model_initial_state, max_weight=1000.)

    self._test_model_curr_inj(nest_model_name, nestml_model_name, gsl_error_tol, tolerance, nest_ref_model_opts, custom_model_opts, model_initial_state)

        all_nestml_neuron_models = [s[:-7] for s in list(os.walk("models/neurons"))[0][2] if s[-7:] == ".nestml"]
        s += self.generate_neuron_models_documentation(neuron_models, all_nestml_neuron_models)

        s += "Synapse models\n~~~~~~~~~~~~~~\n\n"

        synapse_models = []
        synapse_models.append(("static_synapse", "static_synapse.nestml"))
        synapse_models.append(("noisy_synapse", "noisy_synapse.nestml"))
        synapse_models.append(("stdp_synapse", "stdp_synapse.nestml"))
        synapse_models.append(("stdp_nn_pre_centered_synapse", "stdp_nn_pre_centered_synapse.nestml"))
        synapse_models.append(("stdp_nn_restr_symm_synapse", "stdp_nn_restr_symm_synapse.nestml"))
        synapse_models.append(("stdp_nn_symm_synapse", "stdp_nn_symm_synapse.nestml"))
        synapse_models.append(("stdp_triplet_nn_synapse", "triplet_stdp_synapse.nestml"))
        synapse_models.append(("stdp_triplet_synapse", "stdp_triplet_naive.nestml"))
        synapse_models.append(("third_factor_stdp_synapse", "third_factor_stdp_synapse.nestml"))
        synapse_models.append(("neuromodulated_stdp_synapse", "neuromodulated_stdp_synapse.nestml"))

        all_synapse_models = [s[:-7] for s in list(os.walk("models/synapses"))[0][2] if s[-7:] == ".nestml"]
        s += self.generate_synapse_models_documentation(synapse_models, all_synapse_models)

        with open("models_library.rst", "w") as f:
            f.write(s)

    def generate_synapse_models_documentation(self, models, allmodels):
        r"""
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        models : list of tuples
            Tested models and test conditions, in order.
        """

        print("allmodels = " + str(allmodels))

        untested_models = copy.deepcopy(allmodels)
        for model in models:
            model_fname = model[1]
            assert removesuffix(model_fname, ".nestml") in allmodels
            if model_fname in untested_models:
                untested_models.remove(model_fname)
        print("untested_models = " + str(untested_models))

        s = ""

        for model in models:
            model_name = model[0]
            model_fname = model[1]
            model_fname_stripped = removesuffix(model_fname, ".nestml")

            if model_fname_stripped in untested_models:
                untested_models.remove(model_fname_stripped)

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join("models", "synapses", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/synapses/"\
                 + model_fname + ">`_\n"
            s += "\n"

        for model_name in untested_models:
            testant = model_name + "_nestml"
            model_fname = model_name + ".nestml"

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join("models", "synapses", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/synapses/"\
                 + model_fname + ">`_\n"
            s += "\n"

        return s

    def generate_neuron_models_documentation(self, models, allmodels):
        """
        models : list of tuples
            Tested models and test conditions, in order.
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        """

        print("All NESTML neuron models = " + str(allmodels))

        untested_models = copy.deepcopy(allmodels)
        for model in models:
            testant = model[1]
            model_name = testant[:-7]
            model_name.removesuffix("_alt_nestml")
            assert model_name in allmodels
            if model_name in untested_models:
                untested_models.remove(model_name)
        print("Untested NESTML neuron models = " + str(untested_models))

        s = ""

        for model in models:
            reference = model[0]
            testant = model[1]
            gsl_error_tol = model[2]
            tolerance = model[3]

            if testant in untested_models:
                untested_models.remove(testant)

            if len(model) > 4:
                nest_ref_model_opts = model[4]
            else:
                nest_ref_model_opts = {}
            if len(model) > 5:
                custom_model_opts = model[5]
            else:
                custom_model_opts = {}

            model_fname = testant[:-7] + ".nestml"  # strip "_nestml"
            model_name = testant[:-7]

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join("models", "neurons", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/neurons/" \
                 + model_fname + ">`_\n"
            s += "\n"
            s += ".. list-table::\n"
            s += "\n"
            s += "   * - .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library" \
                 "/nestml_models_library_[" + \
                 model_name + "]_synaptic_response_small.png\n"
            s += "          :alt: " + model_name + "\n"
            s += "\n"
            s += "     - .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library" \
                 "/nestml_models_library_[" + \
                 model_name + "]_f-I_curve_small.png\n"
            s += "          :alt: " + model_name + "\n"
            s += "\n"

            with open(model_name + "_characterisation.rst", "w") as f:
                s_ = "Synaptic response\n-----------------\n\n"
                s_ += ".. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library" \
                      "/nestml_models_library_[" + \
                      model_name + "]_synaptic_response.png\n"
                s_ += "   :alt: " + testant + "\n"
                s_ += "\n"
                s_ += "f-I curve\n---------\n\n"
                s_ += ".. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library" \
                      "/nestml_models_library_[" + \
                      model_name + "]_f-I_curve.png\n"
                s_ += "   :alt: " + testant + "\n"
                s_ += "\n"
                f.write(s_)

        for model_name in untested_models:
            testant = model_name + "_nestml"
            model_fname = model_name + ".nestml"

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join("models", "neurons", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/neurons/" \
                 + model_fname + ">`_\n"
            s += "\n"

        return s

    def _test_model_curr_inj(self, nest_model_name, testant, gsl_error_tol, tolerance=0.000001,
                             nest_ref_model_opts=None, custom_model_opts=None, model_initial_state=None):
        """For different levels of injected current, verify that behaviour is the same between NEST and NESTML"""
        t_stop = 1000.  # [ms]

        I_stim_vec = np.linspace(10E-12, 1E-9, 3)  # [A]
        rate_testant = float("nan") * np.ones_like(I_stim_vec)
        rate_reference = float("nan") * np.ones_like(I_stim_vec)
        for i, I_stim in enumerate(I_stim_vec):

            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": .01})    # aeif_cond_exp model requires resolution <= 0.01 ms

            neuron1 = nest.Create(nest_model_name, params=nest_ref_model_opts)
            neuron2 = nest.Create(testant, params=custom_model_opts)
            if model_initial_state is not None:
                nest.SetStatus(neuron1, model_initial_state)
                nest.SetStatus(neuron2, model_initial_state)

            # if gsl_error_tol is not None:
            #     nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

            dc = nest.Create("dc_generator", params={"amplitude": I_stim * 1E12})  # 1E12: convert A to pA

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
                ax[1].plot(ts2, Vms2, label="Testant " + testant)
                for _ax in ax:
                    _ax.legend(loc="upper right")
                    _ax.grid()
                fig.suptitle("Rate: " + str(rate_testant[i]) + " Hz")
                plt.savefig(
                    "/tmp/nestml_nest_integration_test_subthreshold_[" + nest_model_name + "]_[" + testant + "]_["
                                                                                                            "I_stim="
                    + str(I_stim) + "].png")
                plt.close(fig)

        if TEST_PLOTS:
            if len(I_stim_vec) < 20:
                marker = "o"
            else:
                marker = None
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(I_stim_vec * 1E12, rate_reference, marker=marker, label="Reference " + nest_model_name)
            ax[1].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label="Testant " + testant)
            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.grid()
                _ax.set_ylabel("Firing rate [Hz]")
            ax[1].set_xlabel("$I_{inj}$ [pA]")
            plt.savefig("/tmp/nestml_nest_integration_test_subthreshold_[" + nest_model_name + "]_[" + testant + "].png")
            plt.close(fig)

            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label=referenceModel)
                for _ax in ax:
                    _ax.grid()
                    _ax.set_ylabel("Firing rate [Hz]")
                ax[0].set_xlabel("$I_{inj}$ [pA]")
                plt.tight_layout()
                plt.savefig("/tmp/nestml_models_library_[" + nest_model_name + "]_f-I_curve" + fname_snip + ".png")
                plt.close(fig)

    def _test_model_psc(self, nest_model_name, testant, gsl_error_tol, tolerance=None, nest_ref_model_opts=None,
                        custom_model_opts=None, model_initial_state=None, max_weight: float = 10., compare_V_m_traces: bool = True, tolerance_spiketimes: float = 1E-9):

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": .01})    # aeif_cond_exp model requires resolution <= 0.01 ms


        spike_times = np.linspace(100, 200, 11)
        spike_weights = np.linspace(1, max_weight, 11)

        neuron1 = nest.Create(nest_model_name, params=nest_ref_model_opts)
        neuron2 = nest.Create(testant, params=custom_model_opts)

        if model_initial_state is not None:
            nest.SetStatus(neuron1, model_initial_state)
            nest.SetStatus(neuron2, model_initial_state)

        # if gsl_error_tol is not None:
        #     nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

        spikegenerator = nest.Create("spike_generator",
                                     params={"spike_times": spike_times, "spike_weights": spike_weights})

        nest.Connect(spikegenerator, neuron1)
        nest.Connect(spikegenerator, neuron2)

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
            ax[1].plot(ts2, Vms2, label="Testant " + testant)
            ax[1].scatter(spike_recorder2.events["times"], Vms2[0] * np.ones_like(spike_recorder2.events["times"]))
            np.testing.assert_allclose(ts1, ts2)
            ax[2].semilogy(ts2, np.abs(Vms1 - Vms2), label="Error", color="red")
            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_integration_test_[" + nest_model_name + "]_[" + testant + "].png")
            plt.close(fig)

        if TEST_PLOTS:
            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(ts2, Vms2, label=testant)
                for _ax in ax:
                    _ax.grid()
                ax[0].set_xlabel("Time [ms]")
                ax[0].set_ylabel("$V_m$ [mV]")
                plt.tight_layout()
                plt.savefig("/tmp/nestml_models_library_[" + nest_model_name + "]_synaptic_response" + fname_snip + ".png")
                plt.close(fig)

        if compare_V_m_traces:
            # check that V_m timeseries match
            np.testing.assert_allclose(Vms1, Vms2, rtol=tolerance)

        # check that spike times match (if any)
        np.testing.assert_allclose(spike_recorder1.events["times"], spike_recorder2.events["times"], rtol=tolerance_spiketimes)
