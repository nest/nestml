# -*- coding: utf-8 -*-
#
# test_function_parameter_templating.py
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

from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.frontend.pynestml_frontend import generate_target


class TestFunctionParameterTemplating:
    """
    This test is used to test the correct derivation of types when functions use templated type parameters.
    """

    def test(self):
        fname = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "FunctionParameterTemplatingTest.nestml")))
        generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")
        assert len(Logger.get_all_messages_of_level_and_or_node("templated_function_parameters_type_test", LoggingLevel.ERROR)) == 5
