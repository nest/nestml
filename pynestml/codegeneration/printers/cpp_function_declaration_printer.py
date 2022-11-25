# -*- coding: utf-8 -*-
#
# cpp_function_declaration_printer.py
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

from pynestml.meta_model.ast_node import ASTNode
from pynestml.codegeneration.printers.function_printer import FunctionPrinter


class CppFunctionDeclarationPrinter(FunctionPrinter):
    r"""
    Printer for ASTFunction declaration in C++ syntax.
    """

    def print_function(self, node: ASTNode) -> str:
        """
        Returns a nest processable function declaration head, i.e. the part which appears in the .h file.
        :param node: a single function.
        :return: the corresponding string representation.
        """
        from pynestml.meta_model.node import ASTFunction
        from pynestml.symbols.symbol import SymbolKind
        assert (node is not None and isinstance(node, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of node provided (%s)!' % type(node)
        function_symbol = node.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.FUNCTION)
        if function_symbol is None:
            raise RuntimeError('Cannot resolve the method ' + node.get_name())
        declaration = node.print_comment('//') + '\n'
        declaration += self.types_printer.print(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        declaration += node.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            declaration += self.types_printer.print(typeSym)
            if function_symbol.get_parameter_types().index(typeSym) < len(
                    function_symbol.get_parameter_types()) - 1:
                declaration += ', '
        declaration += ') const\n'
        return declaration
