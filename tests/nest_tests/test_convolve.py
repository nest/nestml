# -*- coding: utf-8 -*-
#
# test_convolve.py
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

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestConvolve:
    """
    """

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_convolve(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "ConvolveSpikingNoAttributes.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install(module_name)

        neuron = nest.Create("convolve_spiking_no_attributes_neuron_nestml")
        sg = nest.Create("spike_generator")
        sg.spike_times = [10., 50.]

        nest.Connect(sg, neuron)

        mm = nest.Create("multimeter", {"record_from": ["x"]})
        nest.Connect(mm, neuron)

        nest.Simulate(100.)

        events = mm.get("events")

        import matplotlib.pyplot as plt
        plt.subplots()
        plt.plot(events["times"], events["x"])
        plt.savefig("/tmp/test_convolve.png")

        assert events["x"][-1] == 2E-3
