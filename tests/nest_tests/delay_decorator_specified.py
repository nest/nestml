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

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestDelayDecoratorSpecified:

    neuron_model_name = "iaf_psc_exp_nestml__with_stdp_nestml"
    ref_neuron_model_name = "iaf_psc_exp_nestml_non_jit"

    synapse_model_name = "stdp_nestml__with_iaf_psc_exp_nestml"
    ref_synapse_model_name = "stdp_synapse"

    @pytest.mark.xfail(strict=True)
    def test_delay_decorator_not_specified_results_in_failure(self):
        r"""Generate the model code"""

        jit_codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                      "synapse": "stdp",
                                                      "post_ports": ["post_spikes"]}]}

        files = [os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
                 os.path.join("tests", "invalid", "stdp_synapse_missing_delay_decorator.nestml")]
        # remove ``@nest::delay`` decorator from the file
        with open(os.path.join("models", "synapses", "stdp_synapse.nestml"), "r") as syn_file:
            lines = syn_file.read()
            lines = lines.replace("@nest::delay", "")
            with open(os.path.join("tests", "invalid", "stdp_synapse_missing_delay_decorator.nestml"), "w") as invalid_syn_file:
                invalid_syn_file.writelines(lines)
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             target_path="/tmp/nestml-jit",
                             logging_level="INFO",
                             module_name="nestml_jit_module",
                             suffix="_nestml",
                             codegen_opts=jit_codegen_opts)
