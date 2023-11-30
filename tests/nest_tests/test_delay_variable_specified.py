# -*- coding: utf-8 -*-
#
# delay_decorator_specified.py
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


class TestDelayVariableSpecified:
    r"""Test that forgetting to specify the ``delay_variable`` when using a synapse results in failure to generate code."""

    codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                "synapse": "stdp_synapse",
                                                "post_ports": ["post_spikes"]}]}

    # @pytest.mark.xfail(strict=True)
    # def test_delay_variable_not_specified_results_in_failure(self):
    #     r"""Generate the model code"""

    #     files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
    #              os.path.join("models", "synapses", "stdp_synapse.nestml")]
    #     input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
    #     generate_nest_target(input_path=input_path,
    #                          logging_level="DEBUG",
    #                          suffix="_nestml",
    #                          codegen_opts=TestDelayVariableSpecified.codegen_opts)

    def test_delay_variable_specified_results_in_success(self):
        r"""Generate the model code"""

        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts={**TestDelayVariableSpecified.codegen_opts, **{"delay_variable": "d"}})

        nest.Install("nestmlmodule")
        n = nest.Create("iaf_psc_exp_neuron_nestml__with__stdp_synapse_nestml")
        nest.Connect(n, n, syn_spec={"synapse_model": "stdp_synapse_nestml__for_iaf_psc_exp_neuron_nestml", "d": 42.})
        s = nest.GetConnections(n, n)
        assert s.get()["delay"] == 42.
    
        # TODO: test that the weight variable/parameter can be called "weight"; same for "delay"

        # TODO: test that this works in copymodel

        # TODO: test that this works for Get/SetStatus

        # TODO: test that this works when passing parameters during nest.Connect()