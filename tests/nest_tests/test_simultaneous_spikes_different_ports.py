# -*- coding: utf-8 -*-
#
# test_simultaneous_spikes_different_ports.py
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

import matplotlib.pyplot as plt
import numpy as np
import os
import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestSimultaneousSpikesDifferentPorts:
    """
    Tests the code generation and running a little simulation. Check that the numerical membrane voltage at the end of the simulation is close to a hard-coded numeric value.
    """

    @pytest.mark.parametrize("neuron_name", ["aeif_cond_exp", "iaf_psc_delta"])
    def test_simultaneous_spikes_different_ports(self, neuron_name: str):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", neuron_name + "_neuron.nestml"))))
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        suffix = "_nestml"
        module_name = "nestmlmodule"
        codegen_opts = {}

        generate_nest_target(input_path, target_path,
                             module_name=module_name,
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

        nest.ResetKernel()
        nest.Install(module_name)

        sg_exc = nest.Create("spike_generator", {"spike_times": [10., 20., 30., 40., 50.]})
        sg_exc2 = nest.Create("spike_generator", {"spike_times": [40.]})
        sg_inh = nest.Create("spike_generator", {"spike_times": [20., 40.]})
        # sg_inh = nest.Create("spike_generator", {"spike_times": []})

        neuron_nest = nest.Create(neuron_name)
        neuron_nestml = nest.Create(neuron_name + "_neuron_nestml")
        mm_nest = nest.Create("voltmeter")
        mm_nestml = nest.Create("voltmeter")

        nest.Connect(sg_exc, neuron_nest)
        nest.Connect(sg_exc, neuron_nestml)
        nest.Connect(sg_exc2, neuron_nest)
        nest.Connect(sg_exc2, neuron_nestml)
        nest.Connect(sg_inh, neuron_nest, syn_spec={"weight": -1})
        nest.Connect(sg_inh, neuron_nestml, syn_spec={"weight": -1})

        nest.Connect(mm_nest, neuron_nest)
        nest.Connect(mm_nestml, neuron_nestml)

        nest.Simulate(60.)

        # plot the results

        fig, ax = plt.subplots(nrows=1)

        ax.plot(mm_nest.events["times"], mm_nest.events["V_m"], label="NEST")
        ax.plot(mm_nestml.events["times"], mm_nestml.events["V_m"], label="NESTML")
        ax.legend()

        fig.savefig("/tmp/test_simultaneous_spikes_different_ports.png")

        # test that membrane potential is the same at the end of the simulation

        assert neuron_nestml.V_m != neuron_nestml.E_L
        np.testing.assert_allclose(neuron_nest.V_m, neuron_nestml.V_m)
