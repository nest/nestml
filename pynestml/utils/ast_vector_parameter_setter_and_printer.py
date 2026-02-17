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
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTVectorParameterSetterAndPrinter(ASTPrinter):
    """
    This file is part of the compartmental code generation process.

    Part of vectorized printing.
    """
    def __init__(self):
        super(ASTVectorParameterSetterAndPrinter, self).__init__()
        self.inside_variable = False
        self.vector_parameter = ""
        self.black_list = set()
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

        variable_collector = ASTSimpleVariableCollectorVisitor()

        node.accept(variable_collector)

        all_variables = set(variable_collector.all_variables)

        local_white_list = all_variables - self.black_list

        write_permission = [True] * len(text)

        observe = False
        #if text.find("w") >= 0:
        #    observe = True
        #    breakpoint()

        for var in local_white_list:
            pos = 0
            next_pos = 0
            while pos >= 0:
                pos = next_pos
                pos = text.find(var, pos)
                if pos >= 0:
                    for j in range(pos, pos+len(var)):
                        write_permission[j] = False
                next_pos = pos + len(var)

        if observe:
            breakpoint()

        ordered_black_list = sorted(self.black_list, key=len, reverse=True)
        for var in ordered_black_list:
            pos = 0
            next_pos = 0
            while pos >= 0:
                pos = next_pos
                pos = text.find(var, pos)
                if pos >= 0:
                    overwrite = False
                    for j in range(pos, pos+len(var)):
                        if write_permission[j]:
                            overwrite = True
                    if overwrite:
                        start = pos+len(var)
                        end = pos+len(var)+len(self.vector_parameter)+2
                        text = text[:start] + text[end:]
                        write_permission = write_permission[:pos] + ([False] * len(var)) + write_permission[end:]
                next_pos = pos + len(var)

        if observe:
            breakpoint()

        return text

class ASTSimpleVariableCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTSimpleVariableCollectorVisitor, self).__init__()
        self.inside_variable = False
        self.all_variables = set()

    def visit_variable(self, node):
        self.inside_variable = True
        self.all_variables.add(node.name)

    def endvisit_variable(self, node):
        self.inside_variable = False
