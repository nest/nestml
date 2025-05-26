# -*- coding: utf-8 -*-
#
# ast_vector_parameter_setter_and_printer.py
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

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.nest_variable_printer import NESTVariablePrinter


class ASTVectorParameterSetterAndPrinter(ASTPrinter):
    def __init__(self):
        super(ASTVectorParameterSetterAndPrinter, self).__init__()
        self.inside_variable = False
        self.vector_parameter = ""
        self.printer = None
        self.model = None

    def set_vector_parameter(self, node, vector_parameter=None):
        self.vector_parameter = vector_parameter
        node.accept(self)

    def print(self, node):
        assert isinstance(self.printer._simple_expression_printer._variable_printer, NESTVariablePrinter)

        self.printer._simple_expression_printer._variable_printer.cpp_variable_suffix = ""

        if self.vector_parameter:
            self.printer._simple_expression_printer._variable_printer.cpp_variable_suffix = "[" + self.vector_parameter + "]"

        text = self.printer.print(node)

        self.printer._simple_expression_printer._variable_printer.cpp_variable_suffix = ""

        return text
