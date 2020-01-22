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

import nest
import numpy as np
import os
import unittest
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except:
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
        models.append(("iaf_cond_exp", "iaf_cond_exp_implicit_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_alpha", "iaf_cond_alpha_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_alpha", "iaf_cond_alpha_implicit_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_beta", "iaf_cond_beta_nestml", 1E-3, 1E-3, {"tau_rise_ex" : 1., "tau_decay_ex" : 2., "tau_rise_in" : 1., "tau_decay_in" : 2.}, {"tau_syn_rise_E" : 1., "tau_syn_decay_E" : 2., "tau_syn_rise_I" : 1., "tau_syn_decay_I" : 2.}))        # XXX: TODO: does not work yet when tau_rise = tau_fall (numerical singularity occurs in the propagators)

        models.append(("izhikevich", "izhikevich_nestml", 1E-3, 1))     # large tolerance because NEST Simulator model does not use GSL solver, but simple forward Euler

        models.append(("hh_psc_alpha", "hh_psc_alpha_implicit_nestml", 1E-3, 1E-3))
        models.append(("hh_psc_alpha", "hh_psc_alpha_nestml", 1E-3, 1E-3))

        models.append(("iaf_chxk_2008", "iaf_chxk_2008_nestml", 1E-3, 1E-3))
        models.append(("iaf_chxk_2008", "iaf_chxk_2008_implicit_nestml", 1E-3, 1E-3))

        # --------------

        #models.append(("ht_neuron", "hill_tononi_nestml", None, 1E-3))

        """models.append(("aeif_cond_alpha", "aeif_cond_alpha_implicit_nestml", 1.e-3, 1E-3))
        models.append(("aeif_cond_alpha", "aeif_cond_alpha_nestml", 1.e-3, 1E-3))
        models.append(("aeif_cond_exp", "aeif_cond_exp_implicit_nestml", 1.e-3, 1E-3))
        models.append(("aeif_cond_exp", "aeif_cond_exp_nestml", 1.e-3, 1E-3))
        models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_implicit_nestml", 1.e-3, 1E-3))
        models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_nestml", 1.e-3, 1E-3))
        models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_nestml", 1.e-3, 1E-3))
        models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_implicit_nestml", 1.e-3, 1E-3))
        models.append(("iaf_tum_2000", "iaf_tum_2000_nestml", None, 0.01))
        models.append(("mat2_psc_exp", "mat2_psc_exp_nestml", None, 0.1))"""

        for model in models:
            reference = model[0]
            testant = model[1]
            gsl_error_tol = model[2]
            tolerance = model[3]
            if len(model) > 4:
                nest_ref_model_opts = model[4]
            else:
                nest_ref_model_opts = {}
            if len(model) > 5:
                custom_model_opts = model[5]
            else:
                custom_model_opts = {}

            self._test_model(reference, testant, gsl_error_tol, tolerance, nest_ref_model_opts, custom_model_opts)



    def _test_model(self, referenceModel, testant, gsl_error_tol, tolerance=0.000001, nest_ref_model_opts=None, custom_model_opts=None):

        if nest_ref_model_opts is None:
            nest_ref_model_opts = {}

        if custom_model_opts is None:
            custom_model_opts = {}

        spike_times = [100.0, 200.0]
        spike_weights = [1., -1.]

        nest.ResetKernel()
        neuron1 = nest.Create(referenceModel)
        neuron2 = nest.Create(testant)

        if not (gsl_error_tol is None):
            nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

        spikegenerator = nest.Create('spike_generator',
                                     params={'spike_times': spike_times, 'spike_weights': spike_weights})

        nest.Connect(spikegenerator, neuron1)
        nest.Connect(spikegenerator, neuron2)

        multimeter1 = nest.Create('multimeter')
        multimeter2 = nest.Create('multimeter')

        V_m_specifier = 'V_m'  # 'delta_V_m'
        nest.SetStatus(multimeter1, {"withtime": True, "record_from": [V_m_specifier]})
        nest.SetStatus(multimeter2, {"withtime": True, "record_from": [V_m_specifier]})

        nest.Connect(multimeter1, neuron1)
        nest.Connect(multimeter2, neuron2)

        nest.Simulate(400.0)
        dmm1 = nest.GetStatus(multimeter1)[0]
        Vms1 = dmm1["events"][V_m_specifier]
        ts1 = dmm1["events"]["times"]

        dmm2 = nest.GetStatus(multimeter2)[0]
        Vms2 = dmm2["events"][V_m_specifier]
        ts2 = dmm2["events"]["times"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(ts1, Vms1, label = "Reference " + referenceModel)
            ax[1].plot(ts2, Vms2, label = "Testant " + testant)
            for _ax in ax:
                _ax.legend(loc='upper right')
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_integration_test_[" + referenceModel + "]_[" + testant + "].png")

        for index in range(0, len(Vms1)):
            if abs(Vms1[index] - Vms2[index]) > tolerance \
             or np.isnan(Vms1[index]) \
             or np.isnan(Vms2[index]):
                print(str(Vms1[index]) + " differs from  " + str(Vms2[index]) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
                raise Exception(testant + ": TEST FAILED")

        print(testant + " PASSED")
