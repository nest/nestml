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

from pynestml.visitors.ast_visitor import ASTVisitor

from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbol_table.scope import Scope, ScopeType, Symbol, SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol


class ASTVectorParameterSetterAndPrinter(ASTVisitor):
    def __init__(self, model, printer):
        super(ASTVectorParameterSetterAndPrinter, self).__init__()
        self.inside_variable = False
        self.vector_parameter = ""
        self.printer = printer
        self.model = model
        self.depth = 0

    def visit_variable(self, node):
        self.inside_variable = True
        self.depth += 1
        # print(self.printer.print(node)+" visited")

    def endvisit_variable(self, node):
        # print("depth: " + str(self.depth))
        # print(node.name)
        if self.depth < 2000:
            ast_vec_param = None
            # print("processing: " + self.printer.print(node))
            # print(self.vector_parameter)
            if self.vector_parameter is not None:
                ast_vec_param = ModelParser.parse_variable(self.vector_parameter)
                artificial_scope = Scope(ScopeType(1))
                artificial_symbol = VariableSymbol(element_reference=ast_vec_param, scope=artificial_scope,
                                                   name=self.vector_parameter, vector_parameter=None)
                artificial_scope.add_symbol(artificial_symbol)
                ast_vec_param.update_scope(artificial_scope)
                ast_vec_param.accept(ASTSymbolTableVisitor())

                print("vector param attached: " + self.printer.print(ast_vec_param))

            symbol = node.get_scope().resolve_to_symbol(node.name, SymbolKind.VARIABLE)
            # breakpoint()
            if isinstance(symbol, VariableSymbol):
                print("symbol known")
                symbol.vector_parameter = self.vector_parameter
                if symbol.is_spike_input_port():
                    artificial_scope = Scope(ScopeType(1))
                    artificial_symbol = VariableSymbol(element_reference=node, scope=node.get_scope(),
                                                       name=self.vector_parameter, vector_parameter=None)
                    artificial_scope.add_symbol(artificial_symbol)
                    node.update_scope(artificial_scope)
                    node.accept(ASTSymbolTableVisitor())
            node.set_vector_parameter(ast_vec_param)
            # breakpoint()
            print("resulting variable output: " + self.printer.print(node))
        self.inside_variable = False
        self.depth -= 1

    def set_vector_parameter(self, node, vector_parameter=None):
        self.vector_parameter = vector_parameter
        node.accept(self)

    def print(self, node, vector_parameter=None):
        print("NEW PRINT: \n " + self.printer.print(node) + "\nwith vector param: \n " + str(vector_parameter))
        self.set_vector_parameter(node, vector_parameter)
        text = self.printer.print(node)
        print("Resulting expression: \n " + text + "\n")
        self.set_vector_parameter(node)
        return text
