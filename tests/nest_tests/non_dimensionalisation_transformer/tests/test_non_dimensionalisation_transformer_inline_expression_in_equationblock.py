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


class TestNonDimensionalisationTransformerInlineEquationBlock:
    r"""
    This test checks if the transformer can deal with inline expressions in the equation block
    Additionally there is an exp() in the expression
    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_inline_expression_in_equation_block.nestml")))
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

    def test_inline_expression_in_equationblock(self):
        """
        This test checks if the transformer can deal with inline expressions in the equation block
        Additionally there is an exp() in the expression
        """
        codegen_opts = {
            "quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for voltages not part of the test
                                             "electrical current": "p",  # needed for currents not part of the test
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

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["I_spike_test", "V_m_init"]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        V_m_init = mm.get("events")["V_m_init"]
        I_spike_test = mm.get("events")["I_spike_test"]

        np.testing.assert_allclose(V_m_init, -65)  # should be -65 mV
        np.testing.assert_allclose(I_spike_test, 60)  # should be 60 pA

        lhs_expression_after_transformation = "Inline I_spike_test real"
        rhs_after_expression = "1e12 *((30.0 * 1e-9) * ((-V_m_init * 1e-3) / 130e3) * exp((((-80 * 1e-3)) - ((-20 * 1e-3))) / (3000 * 1e-6)))"
