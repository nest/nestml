# -*- coding: utf-8 -*-
#
# test_parrot_neuron.py
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

import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestParrotNeuron:
    r"""Test a parrot neuron that repeats all spikes received on its first input port. This tests that spikes can be emitted from inside onReceive blocks."""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""
        files = [os.path.join("tests", "nest_tests", "resources", "parrot_neuron.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml")

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_neuron_event_priority(self):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")

        # create spike_generators with these times
        port1_sg = nest.Create("spike_generator",
                               params={"spike_times": [1., 11., 21.]})
        port2_sg = nest.Create("spike_generator",
                               params={"spike_times": [6., 16., 26.]})

        # create parrot neurons and connect spike_generators
        neuron = nest.Create("parrot_neuron_nestml")
        sr = nest.Create("spike_recorder")

        nest.Connect(port1_sg, neuron, "one_to_one", syn_spec={"receptor_type": 1, "delay": 1.})
        nest.Connect(port2_sg, neuron, "one_to_one", syn_spec={"receptor_type": 2, "delay": 1.})
        nest.Connect(neuron, sr)

        nest.Simulate(35.)

        np.testing.assert_allclose(sr.events["times"], [2., 12., 22.])
