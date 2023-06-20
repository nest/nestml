# -*- coding: utf-8 -*-
#
# nestml_model_doc_generator.py
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
import matplotlib.pyplot as plt
import numpy as np
import os
import re

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.string_utils import removeprefix, removesuffix


def get_model_doc_title(model_fname: str):
    with open(model_fname) as f:
        model = f.read()
        return re.compile(r'\"\"\"[^#]*###').search(model).group()[3:-3].strip()


class NESTMLModelDocGenerator:

    def __init__(self):
        self.model_doc_rst = ""

    def generate_all_models(self):
        codegen_opts = {}

        generate_nest_target(input_path=["models/neurons"],
                             target_path="/tmp/nestml-autodoc",
                             logging_level="DEBUG",
                             module_name="nestml_autodoc_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)


    def generate_model_docs(self):
        nest.Install("nestml_autodoc_module")

        self.model_doc_rst += "Models library\n==============\n\n"
        self.model_doc_rst += "Neuron models\n~~~~~~~~~~~~~\n\n"

        self._test("iaf_psc_delta_nestml")
        self._test("iaf_psc_exp_nestml")
        self._test("iaf_psc_alpha_nestml")
        self._test("iaf_cond_exp_nestml")
        self._test("iaf_cond_alpha_nestml")
        self._test("iaf_cond_beta_nestml")
        #self._test("hill_tononi_nestml")
        self._test("izhikevich_nestml")
        self._test("hh_psc_alpha_nestml")
        self._test("aeif_cond_exp_nestml")
        self._test("hh_cond_exp_traub_nestml")
        self._test("iaf_chxk_2008_nestml")
        self._test("iaf_cond_exp_sfa_rr_nestml")
        self._test("iaf_tum_2000_nestml")
        self._test("mat2_psc_exp_nestml")

        all_nestml_neuron_models = [s[:-7] for s in list(os.walk("models/neurons"))[0][2] if s[-7:] == ".nestml"]
        self.model_doc_rst += self.generate_neuron_models_documentation(all_nestml_neuron_models)

        #self.model_doc_rst += "Synapse models\n~~~~~~~~~~~~~~\n\n"

        #synapse_models = []
        #synapse_models.append(("static", "static_synapse.nestml"))
        #synapse_models.append(("noisy_synapse", "noisy_synapse.nestml"))
        #synapse_models.append(("stdp", "stdp_synapse.nestml"))
        #synapse_models.append(("stdp_nn_pre_centered", "stdp_nn_pre_centered.nestml"))
        #synapse_models.append(("stdp_nn_restr_symm", "stdp_nn_restr_symm.nestml"))
        #synapse_models.append(("stdp_nn_symm", "stdp_nn_symm.nestml"))
        #synapse_models.append(("stdp_triplet_nn", "triplet_stdp_synapse.nestml"))
        #synapse_models.append(("stdp_triplet", "stdp_triplet_naive.nestml"))
        #synapse_models.append(("third_factor_stdp", "third_factor_stdp_synapse.nestml"))
        #synapse_models.append(("neuromodulated_stdp", "neuromodulated_stdp.nestml"))

        #all_synapse_models = [s[:-7] for s in list(os.walk("models/synapses"))[0][2] if s[-7:] == ".nestml"]
        #s += self.generate_synapse_models_documentation(synapse_models, all_synapse_models)

        with open("models_library.rst", "w") as f:
            f.write(self.model_doc_rst)

    def _test(self, model_name):
        self._test_model_psp(model_name)
        self._test_model_current_pulse(model_name)
        self._test_model_fI_curve(model_name)


    def _test_model_current_pulse(self, model_name, I_min=-50E-12, I_max=500E-12, N=12, 
                             model_opts=None, model_initial_state=None):
        r"""Make current pulse curve"""
        t_stop = 100.  # [ms]
        t_pulse_start = 10. # [ms]
        t_pulse_stop = 90. # [ms]

        fig, ax = plt.subplots(2, 1)
        I_stim_vec = np.linspace(I_min, I_max, N)
        for i, I_stim in enumerate(I_stim_vec):
            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": .01})    # aeif_cond_exp model requires resolution <= 0.01 ms

            neuron = nest.Create(model_name, params=model_opts)
            if model_initial_state is not None:
                nest.SetStatus(neuron, model_initial_state)

            dc = nest.Create("dc_generator", params={"amplitude": 0.})
            nest.Connect(dc, neuron)

            V_m_specifier = "V_m"
            multimeter = nest.Create("multimeter")
            nest.SetStatus(multimeter, {"record_from": [V_m_specifier]})
            nest.Connect(multimeter, neuron)

            sr = nest.Create("spike_recorder")
            nest.Connect(neuron, sr)

            nest.Simulate(t_pulse_start)
            dc.amplitude = I_stim * 1E12  # 1E12: convert A to pA

            nest.Simulate(t_pulse_stop)
            dc.amplitude = 0.

            nest.Simulate(t_stop - t_pulse_stop)

            dmm = nest.GetStatus(multimeter)[0]
            Vms = dmm["events"][V_m_specifier]
            ts = dmm["events"]["times"]

            ax[0].plot(ts, Vms, label=str(I_stim * 1E12))
            ax[1].plot([0, t_pulse_start, t_pulse_start+1E-12, t_pulse_stop, t_pulse_stop+1E-12, t_stop], [0, 0, I_stim * 1E12, I_stim * 1E12, 0, 0], label=str(I_stim * 1E12))

        for _ax in ax:
            _ax.legend(loc="upper right")
            _ax.grid()
        fig.suptitle("Responses to current pulse")
        plt.savefig("/tmp/nestml_current_pulse_response_[" + model_name + "].png")
        plt.close(fig)


    def _test_model_fI_curve(self, model_name, model_opts=None, model_initial_state=None):
        r"""Make f-I curve"""
        t_stop = 1000.  # [ms]

        I_stim_vec = np.linspace(10E-12, 1E-9, 20)  # [A] XXX: should be 100 points
        rate = float("nan") * np.ones_like(I_stim_vec)
        for i, I_stim in enumerate(I_stim_vec):
            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": .01})    # aeif_cond_exp model requires resolution <= 0.01 ms

            neuron = nest.Create(model_name, params=model_opts)
            if model_initial_state is not None:
                nest.SetStatus(neuron, model_initial_state)

            dc = nest.Create("dc_generator", params={"amplitude": I_stim * 1E12})  # 1E12: convert A to pA
            nest.Connect(dc, neuron)

            V_m_specifier = "V_m"
            multimeter = nest.Create("multimeter")
            nest.SetStatus(multimeter, {"record_from": [V_m_specifier]})
            nest.Connect(multimeter, neuron)

            sr = nest.Create("spike_recorder")
            nest.Connect(neuron, sr)

            nest.Simulate(t_stop)

            dmm = nest.GetStatus(multimeter)[0]
            Vms = dmm["events"][V_m_specifier]
            ts = dmm["events"]["times"]

            rate[i] = nest.GetStatus(sr)[0]["n_events"] / t_stop * 1000

            #fig, ax = plt.subplots(2, 1)
            #ax[0].plot(ts, Vms, label=model_name)
            #for _ax in ax:
                #_ax.legend(loc="upper right")
                #_ax.grid()
            #fig.suptitle("Rate: " + str(rate[i]) + " Hz")
            #plt.savefig("/tmp/nestml_fI_curve_[" + model_name + "]_[I_stim=" + str(I_stim) + "].png")
            #plt.close(fig)

        if len(I_stim_vec) < 20:
            marker = "o"
        else:
            marker = None
            
        for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
            fig, ax = plt.subplots(1, 1, figsize=figsize)
            ax = [ax]
            ax[0].plot(I_stim_vec * 1E12, rate, marker=marker, label=model_name)
            for _ax in ax:
                _ax.grid()
                _ax.set_ylabel("Firing rate [Hz]")
            ax[0].set_xlabel("$I_{inj}$ [pA]")
            plt.tight_layout()
            fig.suptitle("f-I curve")
            plt.savefig("/tmp/nestml_fI_curve_[" + model_name + "]" + fname_snip + ".png")
            plt.close(fig)

    def _test_model_psp(self, model_name, max_weight: float = 10., model_opts=None,
                        model_initial_state=None):

        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": .01})    # aeif_cond_exp model requires resolution <= 0.01 ms

        spike_times = [100., 200.]
        spike_weights = [1., -1.]

        neuron = nest.Create(model_name, params=model_opts)

        if model_initial_state is not None:
            nest.SetStatus(neuron, model_initial_state)

        spikegenerator = nest.Create("spike_generator",
                                     params={"spike_times": spike_times, "spike_weights":   spike_weights})

        nest.Connect(spikegenerator, neuron)

        spike_recorder = nest.Create("spike_recorder")
        nest.Connect(neuron, spike_recorder)

        multimeter = nest.Create("multimeter")

        V_m_specifier = "V_m"
        nest.SetStatus(multimeter, {"record_from": [V_m_specifier]})

        nest.Connect(multimeter, neuron)

        nest.Simulate(400.)

        dmm = nest.GetStatus(multimeter)[0]
        Vms = dmm["events"][V_m_specifier]
        ts = dmm["events"]["times"]

        for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
            fig, ax = plt.subplots(1, 1, figsize=figsize)
            ax = [ax]
            ax[0].plot(ts, Vms, label=model_name)
            for _ax in ax:
                _ax.grid()
            ax[0].set_xlabel("Time [ms]")
            ax[0].set_ylabel("$V_m$ [mV]")
            plt.tight_layout()
            fig.suptitle("Postsynaptic potentials")
            plt.savefig("/tmp/nestml_psp_[" + model_name + "]" + fname_snip + ".png")
            plt.close(fig)

    def generate_synapse_models_documentation(self, models, allmodels):
        r"""
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        models : list of tuples
            Tested models and test conditions, in order.
        """

        untested_models = copy.deepcopy(allmodels)
        for model in models:
            model_fname = model[1]
            assert removesuffix(model_fname, ".nestml") in allmodels
            if model_fname in untested_models:
                untested_models.remove(model_fname)

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

    def generate_neuron_models_documentation(self, model_names):
        s = ""

        for model_name in model_names:
            model_name.removesuffix("_alt_nestml")
            model_name.removesuffix("_nestml")

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
                s_ += "   :alt: " + model_name + " postsynaptic response\n"
                s_ += "\n"
                s_ += "f-I curve\n---------\n\n"
                s_ += ".. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library" \
                      "/nestml_models_library_[" + \
                      model_name + "]_f-I_curve.png\n"
                s_ += "   :alt: " + model_name + " f-I curve\n"
                s_ += "\n"
                f.write(s_)

        #for model_name in untested_models:
            #model_fname = model_name + ".nestml"

            #s += "\n"
            #s += ":doc:`" + model_name + " <" + model_name + ">`" + "\n"
            #s += "-" * len(":doc:`" + model_name + " <" + model_name + ">`") + "\n"

            #model_doc_title = get_model_doc_title(os.path.join("models", "neurons", model_fname))
            #if model_doc_title.startswith(model_name):
                #model_doc_title = removeprefix(model_doc_title, model_name)
                #model_doc_title = removeprefix(model_doc_title, " - ")
            #s += "\n" + model_doc_title + "\n"

            #s += "\n"
            #s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/neurons/" \
                 #+ model_fname + ">`_\n"
            #s += "\n"

        return s


if __name__ == "__main__":
    gen = NESTMLModelDocGenerator()
    #gen.generate_all_models()
    gen.generate_model_docs()
