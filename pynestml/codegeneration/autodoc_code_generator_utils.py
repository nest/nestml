# -*- coding: utf-8 -*-
#
# autodoc_code_generator_utils.py
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
import copy
import os
import re

import nest
import numpy as np

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
    models_input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models"))

    @classmethod
    def generate_all_models(cls):
        codegen_opts = {}
        if NESTTools.detect_nest_version().startswith("v3"):
            codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
            codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"
        codegen_opts = {}

        generate_nest_target(input_path=os.path.join(cls.models_input_path, "neurons"),
                             target_path="/tmp/nestml-autodoc",
                             logging_level="INFO",
                             module_name="nestml_autodoc_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @classmethod
    def generate_docs(cls, target_path):
        nest.ResetKernel()

        try:
            nest.Install("nestml_autodoc_module")
        except Exception:
            cls.generate_all_models()
            nest.Install("nestml_autodoc_module")

        s = "Models library\n==============\n\n"

        s += "Neuron models\n~~~~~~~~~~~~~\n\n"

        neuron_models = ["iaf_psc_delta_neuron_nestml",
                         "iaf_psc_exp_neuron_nestml",
                         "iaf_psc_alpha_neuron_nestml",
                         "iaf_cond_exp_neuron_nestml",
                         "iaf_cond_alpha_neuron_nestml",
                         "iaf_cond_beta_neuron_nestml",
                         "izhikevich_neuron_nestml",
                         "hh_psc_alpha_neuron_nestml",
                         "hh_cond_exp_traub_neuron_nestml",
                         "aeif_cond_exp_neuron_nestml",
                         "aeif_cond_alpha_neuron_nestml"]

        for model in neuron_models:
            cls._test_model_curr_inj(model)
            cls._test_model_psc(model)

        all_nestml_neuron_models = [s[:-7] for s in list(os.walk(os.path.join(cls.models_input_path, "neurons")))[0][2] if s[-7:] == ".nestml"]
        s += cls.generate_neuron_models_documentation(neuron_models, all_nestml_neuron_models, target_path)

        s += "Synapse models\n~~~~~~~~~~~~~~\n\n"

        synapse_models = [("static_synapse", "static_synapse.nestml"), ("noisy_synapse", "noisy_synapse.nestml"),
                          ("stdp_synapse", "stdp_synapse.nestml"),
                          ("stdp_nn_pre_centered_synapse", "stdp_nn_pre_centered_synapse.nestml"),
                          ("stdp_nn_restr_symm_synapse", "stdp_nn_restr_symm_synapse.nestml"),
                          ("stdp_nn_symm_synapse", "stdp_nn_symm_synapse.nestml"),
                          ("stdp_triplet_nn_synapse", "triplet_stdp_synapse.nestml"),
                          ("stdp_triplet_synapse", "stdp_triplet_naive.nestml"),
                          ("third_factor_stdp_synapse", "third_factor_stdp_synapse.nestml"),
                          ("neuromodulated_stdp_synapse", "neuromodulated_stdp_synapse.nestml")]

        all_synapse_models = [s[:-7] for s in list(os.walk(os.path.join(cls.models_input_path, "synapses")))[0][2] if s[-7:] == ".nestml"]
        s += cls.generate_synapse_models_documentation(synapse_models, all_synapse_models, target_path)

        with open(os.path.join(target_path, "models_library.rst"), "w") as f:
            f.write(s)

    @classmethod
    def generate_synapse_models_documentation(cls, models, all_models, target_path):
        r"""
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        models : list of tuples
            Tested models and test conditions, in order.
        """

        print("All synapse models = " + str(all_models))

        untested_models = copy.deepcopy(all_models)
        for model in models:
            model_fname = removesuffix(model[1], ".nestml")
            assert model_fname in all_models
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

            model_doc_title = get_model_doc_title(os.path.join(cls.models_input_path, "synapses", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_name + " <https://www.github.com/nest/nestml/blob/master/models/synapses/" \
                 + model_fname + ">`_\n"
            s += "\n"

        for model in untested_models:
            model_name = removesuffix(model, "_synapse")
            model_fname = model_name + ".nestml"

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join(cls.models_input_path, "synapses", model_name))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_name + " <https://www.github.com/nest/nestml/blob/master/models/synapses/" \
                 + model_fname + ">`_\n"
            s += "\n"

        return s

    @classmethod
    def generate_neuron_models_documentation(cls, models, all_models, target_path):
        """
        models : list of tuples
            Tested models and test conditions, in order.
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        """

        print("All NESTML neuron models = " + str(all_models))

        untested_models = copy.deepcopy(all_models)
        for model in models:
            model_name = removesuffix(model, "_nestml")
            assert model_name in all_models
            if model_name in untested_models:
                untested_models.remove(model_name)
        print("Untested NESTML neuron models = " + str(untested_models))

        s = ""

        for model in models:
            testant = removesuffix(model, "_nestml")
            model_fname = testant + ".nestml"  # strip "_nestml"
            model_name = removesuffix(testant, "_neuron")

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join(cls.models_input_path, "neurons", model_fname))
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

            with open(os.path.join(target_path, model_name + "_characterisation.rst"), "w") as f:
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
                print("Writing to file: ", os.path.join(target_path, model_name + "_characterisation.rst"))
                f.write(s_)

        for model_name in untested_models:
            model_fname = model_name + ".nestml"

            s += "\n"
            s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            model_doc_title = get_model_doc_title(os.path.join(cls.models_input_path, "neurons", model_fname))
            if model_doc_title.startswith(model_name):
                model_doc_title = removeprefix(model_doc_title, model_name)
                model_doc_title = removeprefix(model_doc_title, " - ")
            s += "\n" + model_doc_title + "\n"

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/neurons/" \
                 + model_fname + ">`_\n"
            s += "\n"

        return s

    @classmethod
    def _test_model_curr_inj(cls, testant):
        """For different levels of injected current, verify that behaviour is the same between NEST and NESTML"""
        model_name = removesuffix(removesuffix(testant, "_nestml"), "_neuron")
        t_stop = 1000.  # [ms]

        I_stim_vec = np.linspace(10E-12, 1E-9, 100)  # [A]
        rate_testant = float("nan") * np.ones_like(I_stim_vec)
        for i, I_stim in enumerate(I_stim_vec):

            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": .01})  # aeif_cond_exp model requires resolution <= 0.01 ms

            # Create the neuron
            neuron = nest.Create(testant)

            # Create the dc generator
            dc = nest.Create("dc_generator", params={"amplitude": I_stim * 1E12})  # 1E12: convert A to pA
            nest.Connect(dc, neuron)

            # Create the multimeter
            multimeter = nest.Create("multimeter")
            V_m_specifier = "V_m"  # "delta_V_m"
            nest.SetStatus(multimeter, {"record_from": [V_m_specifier]})
            nest.Connect(multimeter, neuron)

            # Create a spike recorder
            if NESTTools.detect_nest_version().startswith("v2"):
                sd_testant = nest.Create("spike_detector")
            else:
                sd_testant = nest.Create("spike_recorder")

            nest.Connect(neuron, sd_testant)

            # Simulate
            nest.Simulate(t_stop)

            # Read the membrane potential and spike time values
            dmm = nest.GetStatus(multimeter)[0]
            Vms = dmm["events"][V_m_specifier]
            ts = dmm["events"]["times"]

            rate_testant[i] = nest.GetStatus(sd_testant)[0]["n_events"] / t_stop * 1000

        if TEST_PLOTS:
            # Sub-threshold plot
            if len(I_stim_vec) < 20:
                marker = "o"
            else:
                marker = None
            fig, ax = plt.subplots(1, 1)
            ax = [ax]
            ax[0].plot(ts, Vms, label="Testant " + testant)
            for _ax in ax:
                _ax.legend(loc="upper right")
                _ax.grid()
                _ax.set_ylabel("Firing rate [Hz]")
            ax[0].set_xlabel("$I_{inj}$ [pA]")
            plt.savefig(
                "/tmp/nestml_nest_integration_test_subthreshold_[" + model_name + "]_[" + testant + "].png")
            plt.close(fig)

            # F-I curve
            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label="Testant " + testant)
                for _ax in ax:
                    _ax.grid()
                    _ax.set_ylabel("Firing rate [Hz]")
                ax[0].set_xlabel("$I_{inj}$ [pA]")
                plt.tight_layout()
                plt.savefig("/tmp/nestml_models_library_[" + model_name + "]_f-I_curve" + fname_snip + ".png")
                plt.close(fig)

    @classmethod
    def _test_model_psc(cls, testant):
        model_name = removesuffix(removesuffix(testant, "_nestml"), "_neuron")

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": .01})  # aeif_cond_exp model requires resolution <= 0.01 ms

        spike_times = [100.0, 200.0]
        spike_weights = [1., -1.]

        # Create a neuron
        neuron = nest.Create(testant)

        # Create a spike generator with spike times and spike weights
        spikegenerator = nest.Create("spike_generator",
                                     params={"spike_times": spike_times, "spike_weights": spike_weights})
        nest.Connect(spikegenerator, neuron)

        # Create a spike recorder
        spike_recorder2 = nest.Create("spike_recorder")
        nest.Connect(neuron, spike_recorder2)

        # Create a multimeter
        multimeter = nest.Create("multimeter")
        V_m_specifier = "V_m"
        nest.SetStatus(multimeter, {"record_from": [V_m_specifier]})
        nest.Connect(multimeter, neuron)

        # Simulate
        nest.Simulate(400.)

        # Read the membrane potential and spike time values
        dmm = nest.GetStatus(multimeter)[0]
        Vms = dmm["events"][V_m_specifier]
        ts = dmm["events"]["times"]

        # Plot for post-synaptic response
        if TEST_PLOTS:
            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(ts, Vms, label=testant)
                for _ax in ax:
                    _ax.grid()
                ax[0].set_xlabel("Time [ms]")
                ax[0].set_ylabel("$V_m$ [mV]")
                plt.tight_layout()
                plt.savefig(
                    "/tmp/nestml_models_library_[" + model_name + "]_synaptic_response" + fname_snip + ".png")
                plt.close(fig)
