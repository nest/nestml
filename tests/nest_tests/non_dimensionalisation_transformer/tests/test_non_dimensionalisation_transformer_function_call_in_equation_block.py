# -*- coding: utf-8 -*-
#
# test_non_dimensionalisation_transformer_function_call_in_equation_block.py
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
        input_path = os.path.join(
            os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../resources",
                    "test_function_call_in_equation_block.nestml",
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

    def test_exp_in_equationblock(self):
        """
        This test checks if the transformer can deal with functions like exp() in the equation block
        V_m' (s) is a time dependent voltage.

        The target unit for V_exp'(s) is mV as the 1/s is being carried implicitly by declaring the variable with a tick, signifying that it is a derived unit with respect to time
        """
        codegen_opts = {
            "solver": "numeric",
            "quantity_to_preferred_prefix": {
                "electrical potential": "m",  # needed for V_m_init and V_exp'
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
            },
        }
        self.generate_code(codegen_opts)

        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.resolution = 1
        nrn = nest.Create(
            "test_function_call_in_equation_block_transformation_neuron_nestml"
        )
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["V_m"]})
        nest.Connect(mm, nrn)
        nest.Simulate(500.0)

        assert nrn.V_m_init == -65  # mV
        assert nrn.tau_m == 12.85  # mS
        assert nrn.alpha_exp == 2 / (70.0 * 1.0e09)  # 1/V
        V_m_end = mm.get("events")["V_m"]
        np.allclose(V_m_end[0], -67.3, atol=0.05)
