# -*- coding: utf-8 -*-
#
# test_rate_interface_units.py
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
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestRateInterfaceUnits:
    r"""
    Rates (the quantity "1 / time") are stored in 1/ms in the code generated for NEST, so that they are coherent with times in ms, but follow the NEST convention of being set, read and recorded by the user in Hz.
    """

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "RateInterfaceUnitsNeuron.nestml")),
                      os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "RateInterfaceUnitsVectorNeuron.nestml"))]
        generate_nest_target(input_path,
                             target_path="target",
                             logging_level="DEBUG",
                             module_name="nestml_rate_interface_units_module",
                             suffix="_nestml")

    def _reset_kernel(self):
        nest.ResetKernel()
        nest.resolution = .1    # [ms]
        try:
            nest.Install("nestml_rate_interface_units_module")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

    def test_rate_interface_units(self):
        self._reset_kernel()
        nrn = nest.Create("rate_interface_units_neuron_nestml")

        # default values are read in Hz
        np.testing.assert_allclose(nrn.r_param, 5.)
        np.testing.assert_allclose(nrn.r, 20.)
        np.testing.assert_allclose(nrn.r_decaying, 50.)
        np.testing.assert_allclose(nrn.tau, 100.)    # time is in ms

        # values are set in Hz
        nrn.r_param = 10.
        np.testing.assert_allclose(nrn.r_param, 10.)
        nest.SetStatus(nrn, {"r": 30.})
        np.testing.assert_allclose(nest.GetStatus(nrn, "r")[0], 30.)

        # values are recorded in Hz
        mm = nest.Create("multimeter", params={"record_from": ["r", "r_inline", "r_decaying"], "interval": nest.resolution})
        nest.Connect(mm, nrn)
        nest.Simulate(1000.)

        events = mm.get("events")
        np.testing.assert_allclose(events["r"], 30.)
        np.testing.assert_allclose(events["r_inline"], 60.)
        np.testing.assert_allclose(events["r_decaying"], 50. * np.exp(-events["times"] / 100.))

        # internally, rates are coherent with time (in ms): a rate of 10 Hz during 1000 ms gives 10 events
        np.testing.assert_allclose(nrn.n, 10.)

    def test_rate_interface_units_vector(self):
        self._reset_kernel()
        nrn = nest.Create("rate_interface_units_vector_neuron_nestml")

        np.testing.assert_allclose(nrn.r_vec, [3., 3.])
        nrn.r_vec = [4., 6.]
        np.testing.assert_allclose(nrn.r_vec, [4., 6.])

        mm = nest.Create("multimeter", params={"record_from": ["R_VEC_0", "R_VEC_1"], "interval": nest.resolution})
        nest.Connect(mm, nrn)
        nest.Simulate(1000.)

        events = mm.get("events")
        np.testing.assert_allclose(events["R_VEC_0"], 4.)
        np.testing.assert_allclose(events["R_VEC_1"], 6.)

        # internally, rates are coherent with time (in ms): a rate of 6 Hz during 1000 ms gives 6 events
        np.testing.assert_allclose(nrn.n, 6.)
