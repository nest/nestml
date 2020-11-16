# -*- coding: utf-8 -*-
#
# ast_random_number_generator_visitor.py
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

from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.void_type_symbol import VoidTypeSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTRandomNumberGeneratorVisitor(ASTVisitor):
    """
    Visits a single function call and updates its type.
    """

    def __init__(self):
        super(ASTRandomNumberGeneratorVisitor, self).__init__()
        self._norm_rng_is_used = False

    def visit_simple_expression(self, node):
        """
        Visits a single function call as stored in a simple expression and checks to see whether any calls are made to generate a random number. If so, set a flag so that the necessary initialisers can be called at the right time in the generated code.
        """
        assert isinstance(node, ASTSimpleExpression), \
            '(PyNestML.Visitor.FunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(node)
        assert (node.get_scope() is not None), \
            "(PyNestML.Visitor.FunctionCallVisitor) No scope found, run symboltable creator!"
        scope = node.get_scope()
        if node.get_function_call() is None:
            return
        function_name = node.get_function_call().get_name()
        method_symbol = scope.resolve_to_symbol(function_name, SymbolKind.FUNCTION)

        # check if this function exists
        if method_symbol is None:
            code, message = Messages.get_could_not_resolve(function_name)
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            node.type = ErrorTypeSymbol()
            return

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            self._norm_rng_is_used = True
            return
