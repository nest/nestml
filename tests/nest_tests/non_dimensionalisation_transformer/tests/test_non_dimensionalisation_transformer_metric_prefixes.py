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
    Test Metric Prefixes
    These tests will check if the standardized metric prefixes in the range of Giga- to Atto- can be resolved.
    The prefixes Deci- and Deca- are probably little used in a neuroscience context.
    The test for Femto- includes the use of a combined physical type, the "magnetic field strength".

    """

    def generate_code_metric_prefixes(self, codegen_opts=None):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "../resources", "test_metric_prefix_transformation.nestml")))
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


    @pytest.mark.parametrize("para_name, expected", [("para_giga", 500)]) #, ("para_mega", 3300), ("para_kilo", 0.002), ("para_hecto", 102.4), ("para_deca", 2300), ("para_deci", 80), ("para_centi", 6700), ("para_milli", 6700), ("para_micro", 0.002), ("para_nano", 0.011), ("para_pico", 0.003), ("para_femto", 77000), ("para_atto", 0.04)])
    def test_metric_prefixes(self, para_name, expected):
        """
        This test checks if the transformer can deal with all metric prefixes in the range of Giga- to Atto- can be resolved and the corresponding factor found.
        """
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
        self.generate_code_metric_prefixes(codegen_opts)
        assert True

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("non_dimensionalisation_transformer_test_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": [para_name]})

        nest.Connect(mm, nrn)

        nest.Simulate(10.)

        para_nme = mm.get("events")[para_name]

        np.testing.assert_allclose(para_nme, expected)