# -*- coding: utf-8 -*-
#
# test_co_generation_static_synapse.py
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

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


def test_co_generation_static_synapse():
    r"""This tests the case that there is a complex neuron model and a simple synapse model that does not transfer any variables."""

    files = [os.path.join("models", "neurons", "hill_tononi_neuron.nestml"),
             os.path.join("models", "synapses", "static_synapse.nestml")]
    input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
        os.pardir, os.pardir, s))) for s in files]
    generate_nest_target(input_path=input_path,
                         logging_level="INFO",
                         suffix="_nestml",
                         codegen_opts={"neuron_synapse_pairs": [{"neuron": "hill_tononi_neuron",
                                                                 "synapse": "static_synapse"}],
                                       "delay_variable": {"static_synapse": "d"},
                                       "weight_variable": {"static_synapse": "w"}})
