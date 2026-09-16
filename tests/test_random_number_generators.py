# -*- coding: utf-8 -*-
#
# test_random_number_generators.py
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
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode
from tests.test_utils import parse_and_validate_model


class TestRandomNumberGeneratorsInODEs:
    """Tests that random number functions are called only in ``update``, ``onReceive``, and ``onCondition`` block"""

    def test_random_number_generators_in_ODEs(self):
        model = parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "random_number_generators_test.nestml"))))

        assert len(Logger.get_messages(model, LoggingLevel.ERROR, message_code=MessageCode.RANDOM_FUNCTIONS_LEGALLY_USED)) == 6

    def test_random_number_generators_in_neuron(self):
        model = parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "random_functions_illegal_neuron.nestml"))))

        assert len(Logger.get_messages(model, LoggingLevel.ERROR, message_code=MessageCode.RANDOM_FUNCTIONS_LEGALLY_USED)) == 3

    def test_random_number_generators_in_synapse(self):
        model = parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "random_functions_illegal_synapse.nestml"))))

        assert len(Logger.get_messages(model, LoggingLevel.ERROR, message_code=MessageCode.RANDOM_FUNCTIONS_LEGALLY_USED)) == 2
