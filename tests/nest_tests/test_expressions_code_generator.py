# -*- coding: utf-8 -*-
#
# test_expressions_code_generator.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.logger import Logger, LoggingLevel


class TestExpressionsCodeGenerator:
    r"""
    Tests code generated for different types of expressions from NESTML to NEST
    """

    def test_expressions(self):
        input_path = str(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, "resources", "ExpressionTypeTest.nestml"))))
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml")
        assert len(Logger.get_messages(level=LoggingLevel.ERROR)) == 0
