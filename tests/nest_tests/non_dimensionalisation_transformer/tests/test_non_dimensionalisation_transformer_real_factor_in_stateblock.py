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


class TestNonDimensionalisationTransformerStateBlock:
    r"""
    This test checks if state block expressions with
    a RHS with a unit being multiplied by a real factor and
    a LHS with type 'real'
    will get processed correctly
    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_real_factor_in_stateblock.nestml")))
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

    def test_real_factor_in_stateblock(self):
        r"""
        This test checks if state block expressions with
        a RHS with a unit being multiplied by a real factor and
        a LHS with type 'real'
        will get processed correctly
        """
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "1",
                                                         # needed for currents not part of the test
                                                         "electrical capacitance": "1",
                                                         # needed for caps not part of the test
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

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["V_m_init", "U_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_m_init = mm.get("events")["V_m_init"]
        U_m = mm.get("events")["U_m"]

        np.testing.assert_allclose(V_m_init, -65)
        np.testing.asser_allclose(U_m, -13)

        lhs_expression_after_transformation = "U_m real"
        rhs_expression_after_transformation = "b * (V_m_init * 1e-3)"