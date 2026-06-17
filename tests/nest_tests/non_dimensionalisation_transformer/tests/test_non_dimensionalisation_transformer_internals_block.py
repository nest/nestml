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


class TestNonDimensionalisationTransformerInternalsBlock:
    r"""
    This test checks if the transformer can deal with transforming the expressions inside the internals block
    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_internals_block.nestml")))
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

    def test_internals_block(self):

        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                    "electrical current": "1",  # needed for currents not part of the test
                                                    "electrical capacitance": "1",  # needed for caps not part of the test
                                                    "electrical resistance": "M",
                                                    "frequency": "k",
                                                    "power": "M",
                                                    "pressure": "k",
                                                    "length": "1",
                                                    "amount of substance": "1",
                                                    "electrical conductance": "m",
                                                    "inductance": "n",
                                                    "time": "f",
                                                    }
        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_internals_block_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["alpha_n_init"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        alpha_m_init = nrn.get("alpha_m_init")

        # np.testing.assert_allclose(alpha_m_init, -20)  # should be -20

        lhs_expression_after_transformation = "alpha_m_init real"
        rhs_expression_after_transformation = "2 * ( (((V_m_init * 1e-3) / (1e-3))  + 40.))"