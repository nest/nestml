#
# models_library_generator.py
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
import unittest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except ImportError:
    TEST_PLOTS = False


class NestModelsLibraryGenerator(unittest.TestCase):

    def test_generate_models_library(self):
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        models = list()
        models.append(("iaf_chxk_2008", "iaf_chxk_2008_nestml", 1.e-3, 0.001))
        models.append(("iaf_chxk_2008", "iaf_chxk_2008_implicit_nestml", 1.e-3, 0.001))
        models.append(("aeif_cond_alpha", "aeif_cond_alpha_implicit_nestml", 1.e-3, 0.001))
        models.append(("aeif_cond_alpha", "aeif_cond_alpha_nestml", 1.e-3, 0.001))
        models.append(("aeif_cond_exp", "aeif_cond_exp_implicit_nestml", 1.e-3, 0.001))
        models.append(("aeif_cond_exp", "aeif_cond_exp_nestml", 1.e-3, 0.001))
        models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_implicit_nestml", 1.e-3, 0.001))
        models.append(("hh_cond_exp_traub", "hh_cond_exp_traub_nestml", 1.e-3, 0.001))
        models.append(("hh_psc_alpha", "hh_psc_alpha_implicit_nestml", 1.e-3, 0.001))
        models.append(("hh_psc_alpha", "hh_psc_alpha_nestml", 1.e-3, 0.001))
        models.append(("iaf_cond_alpha", "iaf_cond_alpha_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_alpha", "iaf_cond_alpha_implicit_nestml", 1E-3, 1E-3))
        models.append(("iaf_cond_exp", "iaf_cond_exp_nestml", 1.e-3, 0.001))
        models.append(("iaf_cond_exp", "iaf_cond_exp_implicit_nestml", 1.e-3, 0.001))
        models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_nestml", 1.e-3, 0.001))
        models.append(("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_implicit_nestml", 1.e-3, 0.001))
        models.append(("iaf_psc_alpha", "iaf_psc_alpha_nestml", None, 0.001))
        models.append(("iaf_psc_delta", "iaf_psc_delta_nestml", None, 0.001))
        models.append(("iaf_psc_exp", "iaf_psc_exp_nestml", None, 0.01))
        models.append(("iaf_tum_2000", "iaf_tum_2000_nestml", None, 0.01))
        models.append(("izhikevich", "izhikevich_nestml", 1.e-3, 0.5))
        models.append(("mat2_psc_exp", "mat2_psc_exp_nestml", None, 0.1))

        for reference, testant, gsl_error_tol, tollerance in models:
            self._test_model(reference, testant, gsl_error_tol, tollerance)

    def _test_model(self, referenceModel, testant, gsl_error_tol, tolerance=0.000001):
        spike_times = [100.0, 200.0]
        spike_weights = [1., -1.]

        nest.ResetKernel()
        neuron1 = nest.Create(referenceModel)
        neuron2 = nest.Create(testant)

        if gsl_error_tol is not None:
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
            ax[0].plot(ts1, Vms1, label="Reference " + referenceModel)
            ax[1].plot(ts2, Vms2, label="Testant " + testant)
            for _ax in ax:
                _ax.legend(loc='upper right')
                _ax.grid()
            plt.savefig("/tmp/nestml_nest_integration_test_[" + referenceModel + "]_[" + testant + "].png")

        for index in range(0, len(Vms1)):
            if abs(Vms1[index] - Vms2[index]) > tolerance \
                    or np.isnan(Vms1[index]) \
                    or np.isnan(Vms2[index]):
                print(str(Vms1[index]) + " differs from  " + str(Vms2[index])
                      + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
                raise Exception(testant + ": TEST FAILED")

        print(testant + " PASSED")
