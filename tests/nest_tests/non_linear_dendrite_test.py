#
# non_linear_dendrite_test.py
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
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except:
    TEST_PLOTS = False



class NestNonLinearDendriteTest(unittest.TestCase):
    """
    Test for proper reset of synaptic integration after condition is triggered (here, dendritic spike)
    """

    def test_non_linear_dendrite(self):
        MAX_SSE = 1E-12






        ln_state_specifier = 'I_dend'
        log10_state_specifier = 'I_kernel2__X__I_2'









        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")))
        nest_path = "/home/archels/nest-simulator-build"
        target_path = 'target'
        logging_level = 'INFO'
        module_name = 'nestmlmodule'
        store_log = False
        suffix = '_nestml'
        dev = True
        #to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
        install_nest(target_path, nest_path)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_nonlineardendrite_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [10., 20., 30.]})
        nest.Connect(sg, nrn, syn_spec={"receptor_type" : 2, "weight": 30., "delay": 1.})

        mm = nest.Create('multimeter')
        mm.set({"record_from": [ln_state_specifier, log10_state_specifier, "V_m"]})
        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        timevec = mm.get("events")["times"]
        ln_state_ts = mm.get("events")[ln_state_specifier]
        log10_state_ts = mm.get("events")[log10_state_specifier]

        if True:
            if TEST_PLOTS:
                fig, ax = plt.subplots(2, 1)
                ax[0].plot(timevec, ln_state_ts, label = "Referenc")
                ax[1].plot(timevec, log10_state_ts, label = "Testant ")
                for _ax in ax:
                    _ax.legend()
                    _ax.grid()
                plt.savefig("/tmp/nestml_younes.png")

        assert np.all(ln_state_ts == log10_state_ts), "Variable " + str(ln_state_specifier) + " and (internal) variable " + str(log10_state_specifier) + " should measure the same thing, but discrepancy in values occurred."

        tidx = np.argmin((timevec - 35)**2)
        assert np.all(ln_state_ts[tidx:] == 0.), "After dendritic spike, dendritic current should be reset to 0 and stay at 0."
