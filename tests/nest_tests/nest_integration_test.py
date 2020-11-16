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

import copy
import nest
import numpy as np
import os
import unittest
import glob
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class NestIntegrationTest(unittest.TestCase):

    def test_nest_integration(self):
        # N.B. all models are assumed to have been already built (see .travis.yml)

        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestml_allmodels_module")

        models = []

        models.append(("iaf_psc_delta", "iaf_psc_delta_nestml", None, 1E-3))
        models.append(("iaf_psc_exp", "iaf_psc_exp_nestml", None, .01))
        models.append(("iaf_psc_alpha", "iaf_psc_alpha_nestml", None, 1E-3))

        models.append(("iaf_cond_exp", "iaf_cond_exp_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_alpha", "iaf_cond_alpha_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_beta", "iaf_cond_beta_nestml", 1E-3, 1E-3, {"tau_rise_ex": 2., "tau_decay_ex": 10., "tau_rise_in": 2., "tau_decay_in": 10.}, {"tau_syn_rise_E": 2., "tau_syn_decay_E": 10., "tau_syn_rise_I": 2., "tau_syn_decay_I": 10.}))        # XXX: TODO: does not work yet when tau_rise = tau_fall (numerical singularity occurs in the propagators)

        models.append(("izhikevich", "izhikevich_nestml", 1E-3, 1))     # large tolerance because NEST Simulator model does not use GSL solver, but simple forward Euler
        models.append(("hh_psc_alpha", "hh_psc_alpha_nestml", 1E-3, 1E-3))
        models.append(("iaf_chxk_2008", "iaf_chxk_2008_nestml", 1E-3, 1E-3))

        # --------------
        # XXX: TODO!

        # models.append(("aeif_cond_alpha", "aeif_cond_alpha_implicit_nestml", 1.e-3, 1E-3))
        # models.append(("aeif_cond_alpha", "aeif_cond_alpha_nestml", 1.e-3, 1E-3))
        # models.append(("aeif_cond_exp", "aeif_cond_exp_implicit_nestml", 1.e-3, 1E-3))
        # models.append(("aeif_cond_exp", "aeif_cond_exp_nestml", 1.e-3, 1E-3))
        # models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_implicit_nestml", 1.e-3, 1E-3))
        # models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_nestml", 1.e-3, 1E-3))
        # models.append(("ht_neuron", "hill_tononi_nestml", None, 1E-3))
        # models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_nestml", 1.e-3, 1E-3))
        # models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_implicit_nestml", 1.e-3, 1E-3))
        # models.append(("iaf_tum_2000", "iaf_tum_2000_nestml", None, 0.01))
        # models.append(("mat2_psc_exp", "mat2_psc_exp_nestml", None, 0.1))

        for model in models:
            reference = model[0]
            testant = model[1]
            gsl_error_tol = model[2]
            tolerance = model[3]
            if len(model) > 4:
                nest_ref_model_opts = model[4]
            else:
                nest_ref_model_opts = None
            if len(model) > 5:
                custom_model_opts = model[5]
            else:
                custom_model_opts = None

            self._test_model(reference, testant, gsl_error_tol, tolerance, nest_ref_model_opts, custom_model_opts)
            self._test_model_subthreshold(reference, testant, gsl_error_tol, tolerance,
                                          nest_ref_model_opts, custom_model_opts)

        all_models = [s[:-7] for s in list(os.walk("models"))[0][2] if s[-7:] == ".nestml"]
        self.generate_models_documentation(models, all_models)

    def generate_models_documentation(self, models, allmodels):
        """
        allmodels : list of str
            List of all model file names (e.g. "iaf_psc_exp") found in the models directory.
        models : list of tuples
            Tested models and test conditions, in order.
        """

        s = "Models library\n==============\n\n"

        print("allmodels = " + str(allmodels))

        untested_models = copy.deepcopy(allmodels)
        for model in models:
            testant = model[1]
            model_name = testant[:-7]
            assert model_name in allmodels or (model_name[-9:] == "_implicit" and model_name[:-9] in allmodels)
            if model_name in untested_models:
                untested_models.remove(model_name)
        print("untested_models = " + str(untested_models))

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

            '''s += model_name + "\n"
            s += "~" * len(model_name) + "\n"
            s += "\n"
            s += ":doc:`" + model_name + " <" + testant + ">`" + "\n"
            s += "\n"'''

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/" + model_fname + ">`_\n"
            s += "\n"
            s += ".. list-table::\n"
            s += "\n"
            s += "   * - .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library/nestml_models_library_[" + \
                model_name + "]_synaptic_response_small.png\n"
            s += "          :alt: " + model_name + "\n"
            s += "\n"
            s += "     - .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library/nestml_models_library_[" + \
                model_name + "]_f-I_curve_small.png\n"
            s += "          :alt: " + model_name + "\n"
            s += "\n"

            with open(model_name + '_characterisation.rst', 'w') as f:
                s_ = "Synaptic response\n-----------------\n\n"
                s_ += ".. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library/nestml_models_library_[" + \
                    model_name + "]_synaptic_response.png\n"
                s_ += "   :alt: " + testant + "\n"
                s_ += "\n"
                s_ += "f-I curve\n---------\n\n"
                s_ += ".. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/models_library/nestml_models_library_[" + \
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

            s += "\n"
            s += "Source file: `" + model_fname + " <https://www.github.com/nest/nestml/blob/master/models/" + model_fname + ">`_\n"
            s += "\n"

        with open('models_library.rst', 'w') as f:
            f.write(s)

    def _test_model_subthreshold(self, referenceModel, testant, gsl_error_tol, tolerance=0.000001, nest_ref_model_opts=None, custom_model_opts=None):
        t_stop = 1000.   # [ms]

        I_stim_vec = np.linspace(10E-12, 1E-9, 100)  # [A]
        rate_testant = float("nan") * np.ones_like(I_stim_vec)
        rate_reference = float("nan") * np.ones_like(I_stim_vec)
        for i, I_stim in enumerate(I_stim_vec):

            nest.ResetKernel()
            neuron1 = nest.Create(referenceModel, params=nest_ref_model_opts)
            neuron2 = nest.Create(testant, params=custom_model_opts)

            if gsl_error_tol is not None:
                nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

            dc = nest.Create("dc_generator", params={"amplitude": I_stim * 1E12})  # 1E12: convert A to pA

            nest.Connect(dc, neuron1)
            nest.Connect(dc, neuron2)

            multimeter1 = nest.Create('multimeter')
            multimeter2 = nest.Create('multimeter')

            V_m_specifier = 'V_m'  # 'delta_V_m'
            nest.SetStatus(multimeter1, {"record_from": [V_m_specifier]})
            nest.SetStatus(multimeter2, {"record_from": [V_m_specifier]})

            nest.Connect(multimeter1, neuron1)
            nest.Connect(multimeter2, neuron2)

            sd_reference = nest.Create('spike_recorder')
            nest.Connect(neuron1, sd_reference)
            sd_testant = nest.Create('spike_recorder')
            nest.Connect(neuron2, sd_testant)

            nest.Simulate(t_stop)
            dmm1 = nest.GetStatus(multimeter1)[0]
            Vms1 = dmm1["events"][V_m_specifier]
            ts1 = dmm1["events"]["times"]

            dmm2 = nest.GetStatus(multimeter2)[0]
            Vms2 = dmm2["events"][V_m_specifier]
            ts2 = dmm2["events"]["times"]

            rate_testant[i] = sd_testant.n_events / t_stop * 1000
            rate_reference[i] = sd_reference.n_events / t_stop * 1000

            if TEST_PLOTS and False:
                fig, ax = plt.subplots(2, 1)
                ax[0].plot(ts1, Vms1, label="Reference " + referenceModel)
                ax[1].plot(ts2, Vms2, label="Testant " + testant)
                for _ax in ax:
                    _ax.legend(loc='upper right')
                    _ax.grid()
                fig.suptitle("Rate: " + str(rate_testant[i]) + " Hz")
                plt.savefig(
                    "/tmp/nestml_nest_integration_test_subthreshold_[" + referenceModel + "]_[" + testant + "]_[I_stim=" + str(I_stim) + "].png")

        if TEST_PLOTS:
            if len(I_stim_vec) < 20:
                marker = "o"
            else:
                marker = None
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(I_stim_vec * 1E12, rate_reference, marker=marker, label="Reference " + referenceModel)
            ax[1].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label="Testant " + testant)
            for _ax in ax:
                _ax.legend(loc='upper right')
                _ax.grid()
                _ax.set_ylabel("Firing rate [Hz]")
            ax[1].set_xlabel("$I_{inj}$ [pA]")
            plt.savefig("/tmp/nestml_nest_integration_test_subthreshold_[" + referenceModel + "]_[" + testant + "].png")

        if TEST_PLOTS:
            if len(I_stim_vec) < 20:
                marker = "o"
            else:
                marker = None
            for figsize, fname_snip in zip([(8, 5), (4, 3)], ["", "_small"]):
                fig, ax = plt.subplots(1, 1, figsize=figsize)
                ax = [ax]
                ax[0].plot(I_stim_vec * 1E12, rate_testant, marker=marker, label=referenceModel)
                for _ax in ax:
                    _ax.grid()
                    _ax.set_ylabel("Firing rate [Hz]")
                ax[0].set_xlabel("$I_{inj}$ [pA]")
                plt.tight_layout()
                plt.savefig("/tmp/nestml_models_library_[" + referenceModel + "]_f-I_curve" + fname_snip + ".png")

        print(testant + " PASSED")

    def _test_model(self, referenceModel, testant, gsl_error_tol, tolerance=0.000001, nest_ref_model_opts=None, custom_model_opts=None):

        spike_times = [100.0, 200.0]
        spike_weights = [1., -1.]

        nest.ResetKernel()
        neuron1 = nest.Create(referenceModel, params=nest_ref_model_opts)
        neuron2 = nest.Create(testant, params=custom_model_opts)

        if gsl_error_tol is not None:
            neuron2.set({"gsl_error_tol": gsl_error_tol})

        spikegenerator = nest.Create('spike_generator',
                                     params={'spike_times': spike_times, 'spike_weights': spike_weights})

        nest.Connect(spikegenerator, neuron1)
        nest.Connect(spikegenerator, neuron2)

        multimeter1 = nest.Create('multimeter')
        multimeter2 = nest.Create('multimeter')

        V_m_specifier = 'V_m'  # 'delta_V_m'
        multimeter1.set({"record_from": [V_m_specifier]})
        multimeter2.set({"record_from": [V_m_specifier]})

        nest.Connect(multimeter1, neuron1)
        nest.Connect(multimeter2, neuron2)

        nest.Simulate(400.0)
        Vms1 = multimeter1.get("events")[V_m_specifier]
        ts1 = multimeter1.get("events")["times"]

        Vms2 = multimeter2.get("events")[V_m_specifier]
        ts2 = multimeter2.get("events")["times"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(ts1, Vms1, label="Reference " + referenceModel)
            ax[1].plot(ts2, Vms2, label="Testant " + testant)
            for _ax in ax:
                _ax.legend(loc='upper right')
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_integration_test_[" + referenceModel + "]_[" + testant + "].png")

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
                plt.savefig("/tmp/nestml_models_library_[" + referenceModel
                            + "]_synaptic_response" + fname_snip + ".png")

        for index in range(0, len(Vms1)):
            if abs(Vms1[index] - Vms2[index]) > tolerance \
                    or np.isnan(Vms1[index]) \
                    or np.isnan(Vms2[index]):
                print(str(Vms1[index]) + " differs from  " + str(Vms2[index])
                      + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
                raise Exception(testant + ": TEST FAILED")

        print(testant + " PASSED")


if __name__ == "__main__":
    t = NestIntegrationTest()
    t.test_nest_integration()
