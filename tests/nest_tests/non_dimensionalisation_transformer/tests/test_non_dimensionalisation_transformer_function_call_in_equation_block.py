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

class TestNonDimensionalisationTransformerEqationBlock:

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_function_call_in_equation_block.nestml")))
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


    def test_exp_in_equationblock(self):
        """
        This test checks if the transformer can deal with functions like exp() in the equation block
        V_m' (s) is a time dependent voltage
        """
        codegen_opts = {"solver": "numeric",
                        "quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and V_exp'
                                                         # "electrical current": "n",  # needed for I_foo
                                                         # "electrical capacitance": "p",  # needed for C_exp_0
                                                         # "electrical resistance": "M",
                                                         # "frequency": "k",
                                                         # "power": "M",
                                                         # "pressure": "k",
                                                         # "length": "1",
                                                         # "amount of substance": "1",
                                                         # "electrical conductance": "m",
                                                         # "inductance": "n",
                                                         "time": "m",
                                                         }
                        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.resolution = 1
        nrn = nest.Create("test_function_call_in_equation_block_transformation_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["V_m"]})
        nest.Connect(mm, nrn)
        # assert nrn.V_m == -70                           # mV
        # assert nrn.V_m_init == -65                      # mV
        # assert nrn.tau_m == 12.85                       # mS
        assert nrn.alpha_exp == 2 / ((70.0 * 1.0E+09))  # 1/V
        nest.Simulate(500.)
        V_m_end = mm.get("events")["V_m"]
        print("V_m progression:", V_m_end)
        print("stop here and inspect V_m_end")


        # after transformation: V_m real =
        # v_m_declaration_rhs_after_transformation="1.0e3 * (-70 * 1.0E-3)"

        # lhs_expression_after_transformation = "V_exp_der' real"
        # rhs_expression_after_transformation = "1e3 * (((V_m * 1e-3)/ (tau_m * 1e-3)) / (((I_foo * 1e-12) * (1 + exp((alpha_exp * 1e-6) * (V_m_init * 1e-3)))) / (C_exp_0 * 1e-12)))"
