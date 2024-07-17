# -*- coding: utf-8 -*-
#
# ast_vector_parameter_setter.py
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

    def visit_variable(self, node):
        self.inside_variable = True
        #print(self.printer.print(node)+" visited")

    def endvisit_variable(self, node):
        ast_vec_param = None
        print(node.name)
        #print("processing: " + self.printer.print(node))

        if self.vector_parameter is not None:
            ast_vec_param = ModelParser.parse_variable(self.vector_parameter)
            artificial_scope = Scope(ScopeType(1))
            artificial_symbol = VariableSymbol(element_reference=ast_vec_param, scope=artificial_scope,
                                               name=self.vector_parameter, vector_parameter=None)
            artificial_scope.add_symbol(artificial_symbol)
            ast_vec_param.update_scope(artificial_scope)
            ast_vec_param.accept(ASTSymbolTableVisitor())

            symbol = self.model.get_scope().resolve_to_symbol(node.name, SymbolKind.VARIABLE)
            #breakpoint()
            if symbol is not None:
                symbol.vector_parameter = self.vector_parameter
            print("vector param attached: " + self.printer.print(ast_vec_param))

        node.set_vector_parameter(ast_vec_param)
        print("resulting variable output: " + self.printer.print(node))
        self.inside_variable = False

    def set_vector_parameter(self, node, vector_parameter=None):
        self.vector_parameter = vector_parameter
        node.accept(self)

    def print(self, node, vector_parameter=None):
        self.set_vector_parameter(node, vector_parameter)
        text = self.printer.print(node)
        self.set_vector_parameter(node)
        return text

