# -*- coding: utf-8 -*-
#
# test_include_statement.py
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

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.FileStream import FileStream
from antlr4.error.ErrorStrategy import BailErrorStrategy
from pynestml.frontend.pynestml_frontend import generate_target

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser


class TestIncludeStatement:
    def test_include_statement(self):
        fname = os.path.realpath(os.path.join(os.path.dirname("__file__"), "tests", "resources", "IncludeStatementTest.nestml"))
        generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")
