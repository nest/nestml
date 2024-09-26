# -*- coding: utf-8 -*-
#
# nest_random_functions_test.py
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
import os

import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestNestRandomFunctions:
    """
    Tests for random number functions in NEST are declared only in ``update``, ``onReceive``, and ``onConditionBlock`` block
    """

    @pytest.mark.xfail(strict=True, raises=Exception)
    def test_nest_random_function_neuron_illegal(self):
        input_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                   "resources", "random_functions_illegal_neuron.nestml"))
        generate_nest_target(input_path=input_path,
                             target_path="target",
                             logging_level="INFO",
                             suffix="_nestml")

    @pytest.mark.xfail(strict=True, raises=Exception)
    def test_nest_random_function_synapse_illegal(self):
        input_path = [
            os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models", "neurons",
                                          "iaf_psc_exp_neuron.nestml")),
            os.path.realpath(os.path.join(os.path.dirname(__file__),
                                          "resources", "random_functions_illegal_synapse.nestml"))]

        generate_nest_target(input_path=input_path,
                             target_path="target",
                             logging_level="INFO",
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "random_functions_illegal_synapse",
                                                                     "post_ports": ["post_spikes"]}],
                                           "weight_variable": {"stdp_synapse": "w"}})
