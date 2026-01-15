# -*- coding: utf-8 -*-
#
# assign_implicit_conversion_factors_visitor.py
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

from typing import Sequence, Union

from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.variadic_type_symbol import VariadicTypeSymbol
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.logging_helper import LoggingHelper
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor


class UnitTypeFixerVisitor(ASTVisitor):
    r"""
    """

    def visit_simple_expression(self, node: ASTSimpleExpression):
        if node.is_numeric_literal() and node.unitType:

            if node.unitType.is_times or node.unitType.is_div:
                # check rhs
                scope = node.get_scope()
                var = node.unitType.rhs
                assert node.unitType.rhs.is_simple_unit() or node.unitType.rhs.is_pow

                if node.unitType.rhs.is_pow:
                    var_name = node.unitType.rhs.base.unit

                if node.unitType.rhs.is_simple_unit():
                    var_name = node.unitType.rhs.unit

                assert var_name is not None

                var_sym_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)
                if var_sym_resolve:
                    # it's actually a variable and not part of the unitType!
                    parent_node = node.get_parent()
                    assert isinstance(parent_node, ASTExpression)

                    # remove the variable from ``node``
                    new_unit_type = node # XXX: TODO

                    # add the variable as an extra term (* ... or / ...) in ``parent_node``
                    if node.unitType.rhs.is_pow:
                        # construct the new term
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_pow_op=True)
                        base_var_name = node.unitType.rhs.base.unit
                        base_var = ASTNodeFactory.create_ast_variable(base_var_name)
                        base_var_simple_expr = ASTNodeFactory.create_ast_simple_expression(variable=base_var)
                        base_var_expr = ASTExpression(expression=base_var_simple_expr)

                        exponent = node.unitType.rhs.exponent
                        exponent_simple_expr = ASTNodeFactory.create_ast_simple_expression(numeric_literal=exponent)
                        exponent_expr = ASTExpression(expression=exponent_simple_expr)

                        expr_to_be_moved = ASTNodeFactory.create_ast_compound_expression(lhs=base_var_expr, binary_operator=binary_operator, rhs=exponent_expr)

                        # substitute it in the parent class
                        if parent_node.binary_operator.is_times_op:
                            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)

                            new_node = ASTExpression(binary_operator=binary_operator, lhs=new_unit_type, rhs=expr_to_be_moved)

                            if parent_node.lhs == node:
                                parent_node.lhs = new_node
                            elif parent_node.rhs == node:
                                parent_node.rhs = new_node



            import pdb;pdb.set_trace()
