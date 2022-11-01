# -*- coding: utf-8 -*-
#
# cpp_expression_printer.py
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

from typing import Optional, Tuple

from pynestml.codegeneration.printers.function_printer import FunctionPrinter
from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind


class CppFunctionDefinitionPrinter(FunctionPrinter):
    r"""
    Printer for ASTFunction definition in C++ syntax.
    """

    def __init__(self, namespace: str = ""):
        self._namespace = namespace
        super().__init__()

    def print_function(self, node: ASTFunction, prefix: str = "") -> str:
        """
        Returns a nest processable function definition, i.e. the part which appears in the .cpp file.
        :param node: a single function.
        :type node: ASTFunction
        :return: the corresponding string representation.
        """
        function_symbol = node.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.FUNCTION)
        if function_symbol is None:
            raise RuntimeError('Cannot resolve the method ' + node.get_name())
        # first collect all parameters
        params = list()
        for param in node.get_parameters():
            params.append(param.get_name())
        declaration = node.print_comment('//') + '\n'
        declaration += self.types_printer.convert(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        if self._namespace is not None:
            declaration += self._namespace + '::'
        declaration += node.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            # create the type name combination, e.g. double Tau
            declaration += self.types_printer.convert(typeSym) + ' ' + \
                params[function_symbol.get_parameter_types().index(typeSym)]
            # if not the last component, separate by ','
            if function_symbol.get_parameter_types().index(typeSym) < \
                    len(function_symbol.get_parameter_types()) - 1:
                declaration += ', '
        declaration += ') const\n'
        return declaration
