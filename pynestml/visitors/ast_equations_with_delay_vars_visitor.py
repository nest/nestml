# -*- coding: utf-8 -*-
#
# ast_equations_with_delay_vars_visitor.py
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
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTEquationsWithDelayVarsVisitor(ASTVisitor):
    """
    A visitor that converts the delay variables parsed as function calls to ASTVariable and collects all the
    equations that have these delay variables.
    """
    def __init__(self):
        super(ASTEquationsWithDelayVarsVisitor, self).__init__()
        self.equations = list()
        self.has_delay = False

    def visit_simple_expression(self, node: ASTSimpleExpression):
        if node.is_function_call() and ASTUtils.is_function_delay_variable(node.get_function_call()):
            # Create a new ASTVariable
            ast_variable = ASTNodeFactory.create_ast_variable(node.get_function_call().get_name(),
                                                              source_position=node.get_source_position())
            # Get the delay parameter
            delay_parameter = ASTUtils.extract_delay_parameter(node.get_function_call())
            ast_variable.set_delay_parameter(delay_parameter)
            ast_variable.update_scope(node.get_scope())

            # Set the variable in the SimpleExpression node
            node.set_variable(ast_variable)

            # Set the delay parameter in its corresponding variable symbol
            delay_variable_symbol = ASTUtils.get_delay_variable_symbol(node.get_function_call())
            if delay_variable_symbol is None:
                code, message = Messages.get_no_variable_found(node.get_function_call().get_name())
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                   log_level=LoggingLevel.ERROR)
                return

            delay_variable_symbol.set_delay_parameter(delay_parameter)

            # Update scope
            node.get_scope().update_variable_symbol(delay_variable_symbol)

            # Nullify the function call
            node.set_function_call(None)

            self.has_delay = True

    def endvisit_ode_equation(self, node: ASTOdeEquation):
        if self.has_delay:
            self.equations.append(node)
            self.has_delay = False
