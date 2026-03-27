# -*- coding: utf-8 -*-
#
# co_co_parameters_internals_state_declaration_order.py
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

from typing import Optional

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType, VariableSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


def get_variable_block_type(var: ASTVariable) -> Optional[BlockType]:
    r"""
    Determines in which block (state, parameters, or internals) a variable was declared.

    :param var: an ASTVariable node
    :return: the BlockType in which the variable was declared, or None if not found
    """
    # Get the symbol from the variable
    if var.get_scope() is None:
        return None

    symbol = var.get_scope().resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE)

    if symbol is None or not isinstance(symbol, VariableSymbol):
        return None

    # Return the block_type from the symbol
    return symbol.block_type


class CoCoParametersInternalsStateDeclarationOrder:
    r"""
    Variables in the state block are only allowed to refer back to internals and parameters, internals are only allowed to refer back to parameters, and parameters can refer back to neither but need to be defined in a self-contained manner.

    Allowed:

    .. ::

          parameters:
              bar real = 123

          state:
              foo real = bar

    Not allowed:

    .. ::

          parameters:
              bar real = foo

          state:
              foo real = 123

    Not allowed:

    .. ::

          state:
              foo real = 123

          parameters:
              bar real = foo

    """

    @classmethod
    def check_co_co(cls, node: ASTModel):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        node.accept(CoCoParametersDefinedBeforeInternalsDefinedBeforeStateVisitor())


class CoCoParametersDefinedBeforeInternalsDefinedBeforeStateVisitor(ASTVisitor):

    def visit_declaration(self, node: ASTDeclaration):
        """
        Ensures the coco.
        :param node: a single equation object.
        """
        if not isinstance(node.get_parent(), ASTBlockWithVariables):
            # this is a local declaration -- skip
            return

        if node.get_parent().is_parameters:
            block_containing_declaration = BlockType.PARAMETERS
        elif node.get_parent().is_internals:
            block_containing_declaration = BlockType.INTERNALS
        elif node.get_parent().is_state:
            block_containing_declaration = BlockType.STATE
        else:
            # This should not happen, as declarations should only be allowed in parameters, internals, or state blocks
            raise Exception(f"Declaration is not contained in parameters, internals, or state block.")

        # get defining expression
        expr = node.get_expression()
        assert expr is not None, "Could not find defining expression for declaration"

        # grab variables in ``expr``
        variables = []

        def collect_vars(node):
            if isinstance(node, ASTVariable):
                variables.append(node)

        expr.accept(ASTHigherOrderVisitor(visit_funcs=collect_vars))

        # for each variable, check where it is declared
        for var in variables:
            if var.name in PredefinedVariables.get_variables():
                # skip predefined variables
                continue

            block_type = get_variable_block_type(var)

            if block_containing_declaration == BlockType.PARAMETERS and block_type == BlockType.STATE:
                code, message = Messages.get_variable_definition_in_parameters_block_not_allowed_to_refer_to_state_block(str(var))
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
            elif block_containing_declaration == BlockType.PARAMETERS and block_type == BlockType.INTERNALS:
                code, message = Messages.get_variable_definition_in_parameters_block_not_allowed_to_refer_to_internals_block(str(var))
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
            elif block_containing_declaration == BlockType.INTERNALS and block_type == BlockType.STATE:
                code, message = Messages.get_variable_definition_in_internals_block_not_allowed_to_refer_to_state_block(str(var))
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
