# -*- coding: utf-8 -*-
#
# test_nest_random_number_generators.py
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

from pynestml.exceptions.code_generation_exception import CodeGenerationException
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode


class TestNESTRandomNumberGenerators:
    """Tests that when generating code for NEST, random number functions are called only in ``update``, ``onReceive``, and ``onCondition`` blocks"""

    def test_random_number_generators_in_neuron(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "resources", "random_functions_illegal_neuron.nestml")))
        logging_level = "DEBUG"

        try:
            generate_nest_target(input_path,
                                 logging_level=logging_level)
        except CodeGenerationException:
            pass

        assert len(Logger.get_messages("random_functions_illegal_neuron", LoggingLevel.ERROR, message_code=MessageCode.NEST_RANDOM_FUNCTIONS_LEGALLY_USED)) == 3

    def test_random_number_generators_in_synapse(self):
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "neurons", "iaf_psc_delta_neuron.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "resources", "random_functions_illegal_synapse.nestml")))]
        logging_level = "DEBUG"
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                  "synapses": {"random_functions_illegal_synapse": {"post_ports": ["post_spikes"]}}}],
                        "weight_variable": {"random_functions_illegal_synapse": "w"}}

        try:
            generate_nest_target(input_path,
                                 logging_level=logging_level,
                                 codegen_opts=codegen_opts)
        except CodeGenerationException:
            pass

        assert len(Logger.get_messages("random_functions_illegal_synapse__with_iaf_psc_delta_neuron", LoggingLevel.ERROR, message_code=MessageCode.NEST_RANDOM_FUNCTIONS_LEGALLY_USED)) == 2
