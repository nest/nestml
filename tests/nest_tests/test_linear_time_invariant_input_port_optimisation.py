# -*- coding: utf-8 -*-
#
# test_linear_time_invariant_input_port_optimisation.py
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

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

TestLinearTimeInvariantInputPortOptimisation_neuron_types = ["aeif_cond_exp", "iaf_psc_delta"]


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestLinearTimeInvariantInputPortOptimisation:
    """
    Test that the optimisations with the ``linear_time_invariant_spiking_input_ports`` NEST code generator option are working correctly.
    """

    module_name: Optional[str] = None

    @pytest.fixture(scope="module", autouse=True)
    def generate_code(self):
        TestLinearTimeInvariantInputPortOptimisation.module_name = "nestmlmodule"    # unfortunately, pytest only allows us to set static attributes on the class
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", neuron_name + "_neuron.nestml")))) for neuron_name in TestLinearTimeInvariantInputPortOptimisation_neuron_types]
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        suffix = "_nestml"
        codegen_opts = {"linear_time_invariant_spiking_input_ports": ["spike_in_port"]}

        generate_nest_target(input_path, target_path,
                             module_name=TestLinearTimeInvariantInputPortOptimisation.module_name,
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

    @pytest.mark.xfail
    @pytest.mark.parametrize("neuron_name", TestLinearTimeInvariantInputPortOptimisation_neuron_types)
    def test_simultaneous_spikes_different_ports(self, neuron_name: str):
        r"""This is known to not work if there are simultaneous spikes!"""
        spike_times_sg_exc = [10., 20., 30., 40., 50.]
        spike_times_sg_exc2 = [40.]
        spike_times_sg_inh = [20., 40.]
        self.run_experiment(neuron_name,
                            spike_times_sg_exc,
                            spike_times_sg_exc2,
                            spike_times_sg_inh)

    @pytest.mark.xfail
    @pytest.mark.parametrize("neuron_name", TestLinearTimeInvariantInputPortOptimisation_neuron_types)
    def test_simultaneous_spikes_different_ports2(self, neuron_name: str):
        r"""This is known to not work if there are simultaneous spikes!"""
        spike_times_sg_exc = [10., 20., 30., 40., 50.]
        spike_times_sg_exc2 = [0.]
        spike_times_sg_inh = [20., 40.]
        self.run_experiment(neuron_name,
                            spike_times_sg_exc,
                            spike_times_sg_exc2,
                            spike_times_sg_inh)

    @pytest.mark.parametrize("neuron_name", TestLinearTimeInvariantInputPortOptimisation_neuron_types)
    def test_non_simultaneous_spikes_different_ports(self, neuron_name: str):
        spike_times_sg_exc = [10., 20., 30., 40., 50.]
        spike_times_sg_exc2 = [45.]
        spike_times_sg_inh = [25., 55.]
        self.run_experiment(neuron_name,
                            spike_times_sg_exc,
                            spike_times_sg_exc2,
                            spike_times_sg_inh)

    def run_experiment(self, neuron_name, spike_times_sg_exc, spike_times_sg_exc2, spike_times_sg_inh):
        nest.ResetKernel()
        nest.Install(TestLinearTimeInvariantInputPortOptimisation.module_name)

        sg_exc = nest.Create("spike_generator", {"spike_times": spike_times_sg_exc})
        sg_exc2 = nest.Create("spike_generator", {"spike_times": spike_times_sg_exc2})
        sg_inh = nest.Create("spike_generator", {"spike_times": spike_times_sg_inh})

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

        fig.savefig("/tmp/test_simultaneous_spikes_different_ports_[neuron=" + neuron_name + "].png")

        # test that membrane potential is the same at the end of the simulation

        assert neuron_nestml.V_m != neuron_nestml.E_L
        np.testing.assert_allclose(neuron_nest.V_m, neuron_nestml.V_m)
