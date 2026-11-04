# -*- coding: utf-8 -*-
#
# test_unit_conversion.py
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

import os

import nest
import numpy as np

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestUnitConversion:
    r"""Check that values with a physical unit are converted once when they are assigned, added, multiplied, raised to a power, compared or passed in a different unit. Generated code holds a numeric literal in NEST units, for instance ``1 V`` as ``1000.`` (mV), so the conversion factor must not be applied to it again."""

    def test_unit_conversion(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "unit_conversion_neuron.nestml")))
        generate_nest_target(input_path,
                             target_path="target",
                             logging_level="DEBUG",
                             module_name="nestmlmodule",
                             suffix="_nestml")

        nest.ResetKernel()
        nest.resolution = .1    # [ms]
        nest.Install("nestmlmodule")

        nrn = nest.Create("unit_conversion_neuron_nestml")
        nest.Simulate(1.)

        np.testing.assert_allclose(nrn.V_decl, 1000.)    # 1 V = 1000 mV
        np.testing.assert_allclose(nrn.I_e, 1000.)    # 1 nA = 1000 pA
        np.testing.assert_allclose(nrn.V_sum, 1001.)    # 1 mV + 1 V = 1001 mV
        np.testing.assert_allclose(nrn.V_sum_rev, 1001.)
        np.testing.assert_allclose(nrn.V_doc, 5.5)    # 100 pA * 55 MOhm = 5.5 mV
        np.testing.assert_allclose(nrn.V_comp, 1001.)
        np.testing.assert_allclose(nrn.V_ret, 1000.)
        np.testing.assert_allclose(nrn.V_tern, 1000.)
        np.testing.assert_allclose(nrn.V_max, 1000.)
        assert nrn.n_steps == 10000    # 1 s = 10000 steps of 0.1 ms
        np.testing.assert_allclose(nrn.f, 10.)    # 10 s**-1 = 10 Hz
        np.testing.assert_allclose(nrn.f_sum, 11.)    # 1 Hz + 10 s**-1 = 11 Hz
        np.testing.assert_allclose(nrn.V_squared, 4E6)    # (2 V)**2 = 4000000 mV**2
        np.testing.assert_allclose(nrn.V_root, 2000.)    # (4 V**2)**0.5 = 2000 mV
        np.testing.assert_allclose(nrn.g, 20.)    # (50 MOhm)**-1 = 20 nS
        np.testing.assert_allclose(nrn.f_pow, 10.)    # (0.1 s)**-1 = 10 Hz
        np.testing.assert_allclose(nrn.V_product, 2000.)    # 1 mV * (2 V / (1 mV)) = 2000 mV
        np.testing.assert_allclose(nrn.V_quotient, 500.)    # 1 mV / (2 mV / (1 V)) = 500 mV
        np.testing.assert_allclose(nrn.V_floor, 500.)    # 1 mV // (2 mV / (1 V)) = 500 mV
        np.testing.assert_allclose(nrn.f_tern, 1.)    # false ? 1 kHz : 1 Hz = 1 Hz
        np.testing.assert_allclose(nrn.f_min, 0.002)    # min(1 kHz, 2 Hz) = 0.002 kHz
        assert nrn.f_less == 1    # 10 Hz < 50 s**-1
        np.testing.assert_allclose(nrn.I_ode, 2001. * (1. - np.exp(-1.)))    # 1 pA + 2 nA = 2001 pA
