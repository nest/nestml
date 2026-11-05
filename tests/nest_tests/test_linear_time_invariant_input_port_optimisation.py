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
from tests.test_utils import ArrayMismatch, numpy_assert_allclose


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestLinearTimeInvariantInputPortOptimisation:
    """
    Test that the optimisations with the ``linear_time_invariant_spiking_input_ports`` NEST code generator option are working correctly.
    """

    module_name: Optional[str] = None

    def generate_code(self, lti: bool):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
        target_path = "nestmlmodule"
        logging_level = "DEBUG"
        suffix = "_nestml"
        codegen_opts = {}

        if lti:
            codegen_opts["linear_time_invariant_spiking_input_ports"] = ["input_spikes"]

        generate_nest_target(input_path, target_path,
                             module_name="nestmlmodule",
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts=codegen_opts)

    @pytest.mark.xfail(strict=True, raises=ArrayMismatch)
    def test_simultaneous_spikes_different_ports(self):
        r"""This is known to not work if there are simultaneous spikes!"""
        self.generate_code(lti=True)

        spike_times_sg_exc = [10., 20., 30.]
        spike_times_sg_inh = [20.]
        self.run_experiment(spike_times_sg_exc,
                            spike_times_sg_inh,
                            fname_snip="_[lti=True]")

        spike_times_sg_exc = [10., 20., 30.]
        spike_times_sg_inh = [25.]
        self.run_experiment(spike_times_sg_exc,
                            spike_times_sg_inh,
                            fname_snip="_[lti=True]")

    def test_non_simultaneous_spikes_different_ports(self):
        r"""This should work if there are simultaneous spikes!"""
        self.generate_code(lti=False)
        spike_times_sg_exc = [10., 20., 30.]
        spike_times_sg_inh = [20.]
        self.run_experiment(spike_times_sg_exc,
                            spike_times_sg_inh,
                            fname_snip="_[lti=False]")

    def run_experiment(self, spike_times_sg_exc, spike_times_sg_inh, fname_snip=""):
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        sg_exc = nest.Create("spike_generator", {"spike_times": spike_times_sg_exc})
        sg_inh = nest.Create("spike_generator", {"spike_times": spike_times_sg_inh})

        neuron_nest = nest.Create("iaf_psc_exp")
        neuron_nestml = nest.Create("iaf_psc_exp_neuron_nestml")
        neuron_nest.tau_syn_ex = 2.
        neuron_nest.tau_syn_in = 4.
        neuron_nestml.tau_syn_exc = 2.
        neuron_nestml.tau_syn_inh = 4.
        mm_nest = nest.Create("voltmeter")
        mm_nestml = nest.Create("voltmeter")

        nest.Connect(sg_exc, neuron_nest)
        nest.Connect(sg_exc, neuron_nestml)
        nest.Connect(sg_inh, neuron_nest, syn_spec={"weight": -3})
        nest.Connect(sg_inh, neuron_nestml, syn_spec={"weight": -3})

        nest.Connect(mm_nest, neuron_nest)
        nest.Connect(mm_nestml, neuron_nestml)

        nest.Simulate(60.)

        # plot the results

        fig, ax = plt.subplots(nrows=1)

        ax.plot(mm_nest.events["times"], mm_nest.events["V_m"], label="NEST")
        ax.plot(mm_nestml.events["times"], mm_nestml.events["V_m"], label="NESTML")
        ax.legend()

        fig.savefig("/tmp/test_simultaneous_spikes_different_ports" + fname_snip + ".png")

        # test that membrane potential is the same at the end of the simulation

        assert neuron_nestml.V_m != neuron_nestml.E_L
        numpy_assert_allclose(neuron_nest.V_m, neuron_nestml.V_m)
