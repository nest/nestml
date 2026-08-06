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

from pynestml.meta_model.ast_assignment import ASTAssignment
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
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.real_type_symbol import RealTypeSymbol
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
    TODO:
    - do this recursively (in case of unit*var*var/var... etc)
    """

    def _split_off_unit_type_term(self, unit_type, parent_unit_type: ASTUnitType, node):
        assert unit_type.is_simple_unit() or unit_type.is_pow

        var_name = None

        if unit_type.is_pow:
            var_name = unit_type.base.unit

        if unit_type.is_simple_unit():
            var_name = unit_type.unit

        assert var_name is not None

        scope = node.get_scope()
        var_sym_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)
        if var_sym_resolve:
            print("REPLACING IN NODE = " + str(node))
            print("\t old unit type = " + str(parent_unit_type))
            print("\t new unit type = " + str(parent_unit_type.lhs))
            # it's actually a variable and not part of the unitType!

            # remove the variable from ``node``
            new_numeric_literal_expr = ASTSimpleExpression(numeric_literal=node.numeric_literal,
                                                unitType=parent_unit_type.lhs)    # ``node`` is of the form ``lhs * rhs``; remove the entire rhs

            # add the variable as an extra term (* ... or / ...) in ``parent_node``
            if unit_type.is_pow:
                # construct the new term
                binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_pow_op=True)

                base_var_name = unit_type.base.unit
                base_var = ASTNodeFactory.create_ast_variable(base_var_name)
                base_var_simple_expr = ASTNodeFactory.create_ast_simple_expression(variable=base_var)
                base_var_expr = ASTExpression(expression=base_var_simple_expr)

                exponent = unit_type.exponent
                exponent_simple_expr = ASTNodeFactory.create_ast_simple_expression(numeric_literal=abs(exponent))
                if exponent < 0:
                    unary_operator = ASTUnaryOperator(is_unary_minus=True)
                    exponent_expr = ASTExpression(unary_operator=unary_operator, expression=exponent_simple_expr)
                else:
                    exponent_expr = ASTExpression(expression=exponent_simple_expr)
                exponent_expr.type = RealTypeSymbol()
                exponent_simple_expr.type = RealTypeSymbol()

                expr_to_be_moved = ASTNodeFactory.create_ast_compound_expression(lhs=base_var_simple_expr, binary_operator=binary_operator, rhs=exponent_expr)

            elif unit_type.is_simple_unit():
                # construct the new term
                var_name = unit_type.unit
                var = ASTNodeFactory.create_ast_variable(var_name)
                var_simple_expr = ASTNodeFactory.create_ast_simple_expression(variable=var)
                var_expr = ASTExpression(expression=var_simple_expr)
                expr_to_be_moved = var_simple_expr

            else:
                raise Exception("Not implemented yet!")

            # orig_parent_unit_type = copy.deepcopy(parent_unit_type)

            # if parent_unit_type.is_div:
            #     if parent_unit_type.rhs == unit_type or parent_unit_type.rhs.compound_unit == unit_type:
            #         parent_unit_type.unit = parent_unit_type.lhs
            #         parent_unit_type.is_div = False
            #         parent_unit_type.lhs = None
            #         parent_unit_type.rhs = None
            #         print("New parent_unit_type = " + str(parent_unit_type))
            #     else:
            #         raise Exception("not handled!")
            # else:
            #     raise Exception("not handled!")

            parent_node = ASTUtils.find_parent_node_by_type(node, ASTExpression)
            if parent_node:
                # appears inside an expression
                assert parent_node.lhs == node

                if parent_node.get_binary_operator() and parent_unit_type.is_times:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)

                    parent_node.lhs = new_node
                elif parent_node.get_binary_operator() and parent_unit_type.is_div:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)

                    parent_node.lhs = new_node
                    new_node._parent = parent_node

                else:
                    raise Exception("not handled!")

                return

            parent_node = ASTUtils.find_parent_node_by_type(node, ASTAssignment)
            if parent_node:
                # appears on the rhs of an assignment
                # assert node.get_parent().rhs == node

                if parent_unit_type.is_div:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                elif parent_unit_type.is_times:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                else:
                    raise Exception("not handled!")

                parent_node.rhs = new_node
                new_node._parent = parent_node
                print("\tsub done! parent_node = " + str(parent_node))
                return

            # parent_node = node.get_parent()
            # if isinstance(parent_node, ASTExpression):
            #     # substitute the new expression ``expr_to_be_moved`` into the parent class
            #     binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
            #     new_node = ASTExpression(binary_operator=binary_operator, lhs=new_unit_type, rhs=expr_to_be_moved)
            #     if parent_node.binary_operator.is_times_op:
            #         if parent_node.lhs == node:
            #             parent_node.lhs = new_node
            #         elif parent_node.rhs == node:
            #             parent_node.rhs = new_node
            #     elif parent_node.binary_operator.is_div_op:
            #         raise Exception("unhandeled")
            # elif isinstance(parent_node, ASTAssignment):
            #     # appears on the rhs of an assignment
            #     assert node.get_parent().rhs == node
            #     import pdb;pdb.set_trace()
            #     parent_node.rhs = new_node
            # else:
            #     raise Exception("Unhandled node: " + str(parent_node))

    def visit_simple_expression(self, node: ASTSimpleExpression):
        if node.is_numeric_literal() and node.unitType:
            if node.unitType.is_times or node.unitType.is_div:
                if node.unitType.rhs.is_encapsulated:
                    self._split_off_unit_type_term(node.unitType.rhs.compound_unit, node.unitType, node)
                else:
                    self._split_off_unit_type_term(node.unitType.rhs, node.unitType, node)
                print("RETURNING!!!!!!")
                return