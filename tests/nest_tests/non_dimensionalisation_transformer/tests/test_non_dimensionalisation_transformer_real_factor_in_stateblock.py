# -*- coding: utf-8 -*-
#
# test_non_dimensionalisation_transformer_real_factor_in_stateblock.py
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
    This test checks if state block expressions with a RHS with a unit being multiplied by a real factor and a LHS with type 'real' will get processed correctly.

    This test checks if state block expressions with a RHS with a unit being multiplied by a real factor a LHS with type 'real' will get processed correctly.

    The target unit JSON file is
    ```JSON
    {"quantity_to_preferred_prefix":
        {
        "electrical potential": "m",    # needed for V_m_init and U_m
        "electrical current": "1",      # needed for currents not part of the test
        "electrical capacitance": "1",  # needed for caps not part of the test
        }
    }
    ```
    Before the transformation the relevant .NESTML should read

    ```NESTML
        state:
            U_m real = b * V_m_init          # Membrane potential recovery variable

        parameters:
            b real = 0.2                     # sensitivity of recovery variable
            V_m_init mV = -65 mV             # Initial membrane potential
    ```
    After the transformation it should read
    ```NESTML
        state:
            U_m real = b * V_m_init          # Membrane potential recovery variable

        parameters:
            b real = 0.2                     # sensitivity of recovery variable
            V_m_init real = 1e3 * (-65e-3)   # Initial membrane potential
    ```

    """

    def generate_code(self, codegen_opts=None):
        input_path = os.path.join(
            os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../resources",
                    "test_real_factor_in_state_block.nestml",
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

    def test_real_factor_in_stateblock(self):
        r"""
        This test checks if state block expressions with
        a RHS with a unit being multiplied by a real factor and
        a LHS with type 'real'
        will get processed correctly
        """
        codegen_opts = {
            "quantity_to_preferred_prefix": {
                "electrical potential": "k",  # needed for V_m_init and U_m
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

        nrn = nest.Create(
            "test_real_factor_in_state_block_transformation_neuron_nestml"
        )
        mm = nest.Create("multimeter")

        nest.Connect(mm, nrn)

        nest.Simulate(10.0)

        V_m_init = nrn.get("V_m_init")

        np.testing.assert_allclose(V_m_init, -65e-6)
