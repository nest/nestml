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
import re
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestNonDimensionalisationTransformerStateBlock:
    r"""
    This test checks if the transformer can deal with reciprocal units on the LHS of an equation inside the parameter block
    TODO: The grammar needs to be changed for reciprocal units to be accepted on LHSs
    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_reciprocal_units_in_parameter_block.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = ""

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

    def test_reciprocal_unit_in_parameterblock(self):

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

        # nest.ResetKernel()
        # nest.Install("nestmlmodule")
        #
        # nrn = nest.Create("test_reciprocal_units_in_parameter_block_transformation_neuron")
        # mm = nest.Create("multimeter")
        # nest.SetStatus(mm, {"record_from": ["alpha_exp"]})
        #
        # nest.Connect(mm, nrn)
        #
        # nest.Simulate(10.)
        #
        # alpha_exp = mm.get("events")["alpha_exp"]
        #
        # np.testing.assert_allclose(alpha_exp, 6.667e-10)  # should be (2e-10/3) (1/mV)

        lhs_expression_after_transformation_parameter = "alpha_exp real"
        rhs_expression_after_transformation_parameter = "2 / (3.0 * 1.0E+06)"

        with open("transformed_model.txt") as file:
            lines = file.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].lstrip()
        for line in lines:
            if line.startswith("alpha_exp 1/V ="):
                start = '= '
                end = ' #'
                transformed_rhs = re.search('%s(.*)%s' % (start, end), line).group(1)
        assert(transformed_rhs == rhs_expression_after_transformation_parameter)
        print("stop")
