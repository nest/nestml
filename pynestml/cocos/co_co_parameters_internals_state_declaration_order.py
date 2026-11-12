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

from typing import Any, Dict, List, Optional, Set

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType, VariableSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoParametersInternalsStateDeclarationOrder(CoCo):
    r"""
    Definitions of variables in the ``state`` block are allowed to refer to variables from the ``parameters`` and ``internals`` blocks; definitions in the ``internals`` block are only allowed to refer to variables from the ``parameters`` block; definitions in the ``parameters`` block may refer to neither ``state`` nor ``internals`` variables, but have to be self-contained.

    References that go through an inline expression are followed, so that e.g. a parameter cannot indirectly depend on a state variable via an inline expression.

    Allowed:

    .. code-block:: nestml

       parameters:
           bar real = 123

       state:
           foo real = bar

    Not allowed:

    .. code-block:: nestml

       state:
           foo real = 123

       parameters:
           bar real = foo

    Not allowed:

    .. code-block:: nestml

       state:
           foo real = 123

       internals:
           bar real = foo

    Not allowed:

    .. code-block:: nestml

       internals:
           foo real = 123

       parameters:
           bar real = foo
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        node.accept(CoCoParametersInternalsStateDeclarationOrderVisitor())


class CoCoParametersInternalsStateDeclarationOrderVisitor(ASTVisitor):
    r"""
    Visits all declarations in the ``parameters``, ``internals`` and ``state`` blocks and checks whether their defining expressions only refer to variables from blocks that they are allowed to refer to.
    """

    # for each type of block, the types of block that its definitions are not allowed to refer to
    _forbidden_references = {
        BlockType.PARAMETERS: {BlockType.INTERNALS, BlockType.STATE},
        BlockType.INTERNALS: {BlockType.STATE},
        BlockType.STATE: set()
    }

    def visit_declaration(self, node: ASTDeclaration) -> None:
        """
        Checks the coco on the current declaration.
        :param node: a single declaration.
        """
        block = node.get_parent()
        if not isinstance(block, ASTBlockWithVariables):
            # this is a local declaration (for instance, in the update block or in a function) -- skip
            return

        if block.is_parameters:
            block_containing_declaration = BlockType.PARAMETERS
        elif block.is_internals:
            block_containing_declaration = BlockType.INTERNALS
        else:
            assert block.is_state
            block_containing_declaration = BlockType.STATE

        forbidden_block_types = self._forbidden_references[block_containing_declaration]
        if not forbidden_block_types:
            return

        if node.get_expression() is None:
            # no defining expression (for instance, ``foo real`` without initial value)
            return

        already_reported: Set[str] = set()
        for var, symbol in self._collect_referenced_variable_symbols(node.get_expression()):
            if symbol.block_type not in forbidden_block_types:
                continue

            if symbol.get_symbol_name() in already_reported:
                continue

            already_reported.add(symbol.get_symbol_name())

            if block_containing_declaration == BlockType.PARAMETERS and symbol.block_type == BlockType.STATE:
                code, message = Messages.get_variable_definition_in_parameters_block_not_allowed_to_refer_to_state_block(symbol.get_symbol_name())
            elif block_containing_declaration == BlockType.PARAMETERS and symbol.block_type == BlockType.INTERNALS:
                code, message = Messages.get_variable_definition_in_parameters_block_not_allowed_to_refer_to_internals_block(symbol.get_symbol_name())
            else:
                assert block_containing_declaration == BlockType.INTERNALS and symbol.block_type == BlockType.STATE
                code, message = Messages.get_variable_definition_in_internals_block_not_allowed_to_refer_to_state_block(symbol.get_symbol_name())

            Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)

    @classmethod
    def _collect_referenced_variable_symbols(cls, expr: ASTExpressionNode) -> List:
        r"""
        Collect all variables referenced in ``expr``, together with their symbols. References to inline expressions are followed (transitively), and the variables referenced in the inline expression's defining expression are included in the result.

        Variables that cannot be resolved (for instance, physical units, or variables that are not defined, which is reported by a different coco) and predefined variables are skipped.

        :param expr: the expression to search for variable references
        :return: a list of tuples ``(variable, symbol)``
        """
        result = []
        visited_inline_expressions: Set[str] = set()
        exprs_to_visit = [expr]

        while exprs_to_visit:
            variables: List[ASTVariable] = []

            def collect_vars(_node):
                if isinstance(_node, ASTVariable):
                    variables.append(_node)

            exprs_to_visit.pop().accept(ASTHigherOrderVisitor(visit_funcs=collect_vars))

            for var in variables:
                if var.get_name() in PredefinedVariables.get_variables():
                    continue

                if var.get_scope() is None:
                    continue

                symbol = var.get_scope().resolve_to_symbol(var.get_name(), SymbolKind.VARIABLE)
                if symbol is None or not isinstance(symbol, VariableSymbol):
                    continue

                if symbol.is_inline_expression:
                    if symbol.get_symbol_name() not in visited_inline_expressions and symbol.get_declaring_expression() is not None:
                        visited_inline_expressions.add(symbol.get_symbol_name())
                        exprs_to_visit.append(symbol.get_declaring_expression())

                    continue

                result.append((var, symbol))

        return result
