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
        codegen_opts = {"quantity_to_preferred_prefix": {"V": preffered_prefix}}
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["V_1", "V_2"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_1 = mm.get("events")["V_1"]
        V_2 = mm.get("events")["V_2"]

        if preffered_prefix == "1":
            # we want representation in Volt
            np.testing.assert_allclose(V_1, -0.07)
            np.testing.assert_allclose(V_2, -0.07)
        elif preffered_prefix == "m":
            # we want representation in milli-Volt
            np.testing.assert_allclose(V_1, -70)
            np.testing.assert_allclose(V_2, -70)
