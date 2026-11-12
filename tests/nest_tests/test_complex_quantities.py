# -*- coding: utf-8 -*-
#
# test_complex_quantities.py
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

from astropy import units as u

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestComplexQuantities:
    r"""
    Physical quantities that are combined using powers (including negative and fractional powers), products and quotients are converted correctly into the units used by NEST: the preferred units (mV, ms, pA, nS, ...) and their products and powers, except for rates, which are exchanged with the user in Hz.

    The expected values are computed independently using astropy, from the literals in the model ``resources/ComplexQuantitiesNeuron.nestml``.
    """

    # parameter values as given in the model
    a_1 = 2 * (u.V / u.s)**-0.5
    a_2 = 2 * (u.V / u.ms)**-0.5
    b_sqrt_rate = 4 * (u.nS / u.uF)**0.5
    c = 3 * u.mV / u.ms

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "ComplexQuantitiesNeuron.nestml"))
        generate_nest_target(input_path,
                             target_path="target",
                             logging_level="DEBUG",
                             module_name="nestml_complex_quantities_module",
                             suffix="_nestml")

    def test_complex_quantities(self):
        nest.ResetKernel()
        nest.resolution = .1    # [ms]
        try:
            nest.Install("nestml_complex_quantities_module")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        nrn = nest.Create("complex_quantities_neuron_nestml")

        # parameters, in NEST units
        np.testing.assert_allclose(nrn.a_1, self.a_1.to((u.mV / u.ms)**-0.5).value)
        np.testing.assert_allclose(nrn.a_2, self.a_2.to((u.mV / u.ms)**-0.5).value)
        np.testing.assert_allclose(nrn.b_sqrt_rate, self.b_sqrt_rate.to(u.ms**-0.5).value)
        np.testing.assert_allclose(nrn.c, self.c.to(u.mV / u.ms).value)

        # initial values of state variables, computed from the parameters
        np.testing.assert_allclose(nrn.rate_y, (self.b_sqrt_rate**2).to(u.Hz).value)    # rates are exchanged with the user in Hz
        np.testing.assert_allclose(nrn.t_half, (self.a_2 * (1 * u.mV)**0.5).to(u.ms**0.5).value)
        np.testing.assert_allclose(nrn.s_1, self.a_1.to((u.mV / u.ms)**-0.5).value)

        # values set by the user are in NEST units as well
        nrn.a_1 = 3.    # [(mV / ms)**-(1/2)]
        np.testing.assert_allclose(nrn.a_1, 3.)
        nrn.a_1 = self.a_1.to((u.mV / u.ms)**-0.5).value

        mm = nest.Create("multimeter", params={"record_from": ["w", "s_1", "rate_y", "t_half"], "interval": nest.resolution})
        nest.Connect(mm, nrn)
        nest.Simulate(20.)

        events = mm.get("events")

        # w' = -w / (a_1**2 * 1 mV): the time constant follows from a quantity raised to a fractional power
        tau = (self.a_1**2 * 1 * u.mV).to(u.ms).value
        np.testing.assert_allclose(tau, 4.)
        np.testing.assert_allclose(events["w"], np.exp(-events["times"] / tau), rtol=1E-6)

        # s_1 = 3 * a_2 in the update block
        np.testing.assert_allclose(events["s_1"], (3 * self.a_2).to((u.mV / u.ms)**-0.5).value)

        # unchanged state variables are recorded in NEST units (rates in Hz)
        np.testing.assert_allclose(events["rate_y"], (self.b_sqrt_rate**2).to(u.Hz).value)
        np.testing.assert_allclose(events["t_half"], (self.a_2 * (1 * u.mV)**0.5).to(u.ms**0.5).value)
