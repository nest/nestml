# -*- coding: utf-8 -*-
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
except Exception:
    TEST_PLOTS = False


class NestNonLinearDendriteTest(unittest.TestCase):
    """
    Test for proper reset of synaptic integration after condition is triggered (here, dendritic spike).
    """

    def test_non_linear_dendrite(self):
        MAX_SSE = 1E-12

        I_dend_alias_name = 'I_dend'
        I_dend_internal_name = 'I_kernel2__X__I_2'

        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")), "iaf_psc_exp_nonlineardendrite.nestml")
        nest_path = "/home/travis/nest_install"
        target_path = 'target'
        logging_level = 'INFO'
        module_name = 'nestmlmodule'
        store_log = False
        suffix = '_nestml'
        dev = True
        to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev)
        install_nest(target_path, nest_path)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_nonlineardendrite_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [10., 20., 30.]})
        nest.Connect(sg, nrn, syn_spec={"receptor_type": 2, "weight": 30., "delay": 1.})

        mm = nest.Create('multimeter')
        mm.set({"record_from": [I_dend_alias_name, I_dend_internal_name]})
        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        timevec = mm.get("events")["times"]
        I_dend_alias_ts = mm.get("events")[I_dend_alias_name]
        I_dend_internal_ts = mm.get("events")[I_dend_internal_name]

        if True:
            if TEST_PLOTS:
                fig, ax = plt.subplots(2, 1)
                ax[0].plot(timevec, I_dend_alias_ts, label="aliased I_dend")
                ax[1].plot(timevec, I_dend_internal_ts, label="internal I_dend")
                for _ax in ax:
                    _ax.legend()
                    _ax.grid()
                plt.ylabel("Dendritic current $I_{dend}$")
                plt.suptitle("Reset of synaptic integration after dendritic spike")
                plt.savefig("/tmp/nestml_younes.png")

        assert np.all(I_dend_alias_ts == I_dend_internal_ts), "Variable " + str(I_dend_alias_name) + " and (internal) variable " + str(I_dend_internal_name) + " should measure the same thing, but discrepancy in values occurred."

        tidx = np.argmin((timevec - 35)**2)
        assert np.all(I_dend_alias_ts[tidx:] == 0.), "After dendritic spike, dendritic current should be reset to 0 and stay at 0."
