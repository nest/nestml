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
    This test checks if the transformer can deal with inline expressions in the equation block. Additionally there is an exp() in the expression.

    The target unit JSON file is
    ```JSON
    {"quantity_to_preferred_prefix":
        {
        "electrical potential": "m",    # needed for V_m_init
        "electrical current": "p",      # needed for I_spike_test
        "electrical capacitance": "1",  # needed for caps not part of the test
        }
    }
    ```

    Before the transformation the relevant .NESTML should read
    ```NESTML
        equations:
            inline I_spike_test A = 30.0 nS * (-V_m_init / 130e3) * exp(((-80 mV) - (-20 mV)) / 3000 uV)

        parameters:
            V_m_init mV = -65 mV     # Initial membrane potential
    ```

    After the transformation it should read
    ```NESTML
        equations:
            inline I_spike_test real = 1e12 * ((30.0 * 1e-9) * ((-V_m_init * * 1e-3)/ 130e3) * exp(((-80 * 1e-3) - (-20 * 1e-3)) / (3000 * 1e-6)))

        parameters:
            V_m_init real = 1e3 * (-65 * 1e-3)     # Initial membrane potential
    ```
    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(
            os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../resources",
                    "test_inline_expression_in_equation_block.nestml",
                )
            )
        )
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(
            input_path,
            target_path=target_path,
            logging_level=logging_level,
            module_name=module_name,
            suffix=suffix,
            codegen_opts=codegen_opts,
        )

    def test_inline_expression_in_equationblock(self):
        """
        This test checks if the transformer can deal with inline expressions in the equation block
        Additionally there is an exp() in the expression
        """
        codegen_opts = {
            "quantity_to_preferred_prefix": {
                "electrical potential": "m",  # needed for voltages not part of the test
                "electrical current": "m",  # needed for currents not part of the test
                "electrical conductance": "m",
                "time": "m",
            }
        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nrn = nest.Create(
            "test_inline_expression_in_equation_block_transformation_neuron_nestml"
        )
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["I_test"]})
        nest.Connect(mm, nrn)
        nest.Simulate(10.0)

        I_spike = 2.718279110177217  # slope
        I0 = 1  # t(0) value
        t_ms = 9.0  # t end
        expected = I0 + I_spike * t_ms  # expected value

        assert np.allclose(mm.get("events")["I_test"][8], expected, atol=1e-9)
