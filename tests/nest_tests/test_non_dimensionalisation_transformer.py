# -*- coding: utf-8 -*-
#
# test_non_dimensionalisation_transformer.py
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
import scipy as sp
import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestNonDimensionalisationTransformer:

    r"""

    CASE 1:

        >>>>> in combination with preferred prefix for CONDUCTANCE = nano
        >>>>> in combination with preferred prefix for CURRENT = milli
        >>>>> in combination with preferred prefix for VOLTAGE = M (megavolt)

        I_foo A = 42 mA
        V_3 V = I_foo / 5 nS

            ---> we expect I_foo to be 42 mA
            ---> we expect "float I_foo" to be 42

            ---> we expect V_3 to be 8.4 MV
            ---> we expect "float V_3 = 8.4"


    CASE 2:

        >>>>> in combination with preferred prefix for CONDUCTANCE = nano
        >>>>> in combination with preferred prefix for CURRENT = 1 (ampere)
        >>>>> in combination with preferred prefix for VOLTAGE = M (megavolt)

        I_foo A = 42 mA
        V_3 V = I_foo / 5 nS

            ---> we expect I_foo to be 42 mA
            ---> we expect "float I_foo" to be 0.042

            ---> we expect V_3 to be 8.4 MV
            ---> we expect "float V_3 = 8.4"



        For each variable and for each numeric literal: multiply by its preferred prefix; then result will be in SI units!

        V_3 V = I_foo / 5 nS
              = (42 * 1E-3) / (5 * 1E-9)   # in Volt
              = 8.4E6  # in Volt

        Then divide the whole thing by preferred prefix of left-hand side variable, in this case, Mega (1E6):

              = 8.4E6 / 1E6
              = 8.4


    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "non_dimensionalisation_transformer_test_neuron.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

    @pytest.mark.parametrize("preffered_prefix", ["1", "m"])
    def test_non_dimensionalisation_transformer(self, preffered_prefix: str):
        codegen_opts = {"quantity_to_preferred_prefix": {"V": "M",
                                                         "I": preffered_prefix}}
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["I_foo", "V_3"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        I_foo = mm.get("events")["I_foo"]
        V_3 = mm.get("events")["V_3"]

        if preffered_prefix == "1":
            # we want representation in Ampère
            np.testing.assert_allclose(I_foo, 0.042)
        elif preffered_prefix == "m":
            # we want representation in mA
            np.testing.assert_allclose(I_foo, 42)

        np.testing.assert_allclose(V_3, 8.4)
