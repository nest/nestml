# -*- coding: utf-8 -*-
#
# unit_type_fixer_visitor.py
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

from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class UnitTypeFixerVisitor(ASTVisitor):
    r"""
    There can be ambiguities during parsing between what is a variable and what is a unit type. E.g. in an expression ``unit*unit**2*var*var/var``. During parsing, this whole expression gets recognised as an ``ASTUnitType``. This visitor takes variables out of ``ASTUnitType``s.

    For instance, given

    .. code:: nestml

       parameters:
           foo real = 42

    the expression

    .. code:: nestml

       42 pA/foo

    will initially be parsed as a numeric literal with a unit type of "pA/foo". However, "foo" actually refers to a parameter in the model. This situation is further exacerbated by NESTML allowing variables to be defined with the same name as units; for instance, there could be a variable defined with the name "mV".

    This visitor tries to resolve the rightmost term in an ASTUnitType as a variable. If it can be resolved, the term is split off, in this example resulting in the expression

    .. code:: nestml

       42 pA / foo

    where the numeric literal has units "pA" and is subsequently divided by the variable "foo".
    """

    @classmethod
    def fix_model(cls, model: ASTModel):
        # keep calling the UnitTypeFixerVisitor until no more changes are made. This is a bit of a hack, but the visitor "eats off" terms one-by-one from the right-hand side of expressions that needs conversion into ``ASTDataType``s.
        model_copy = None
        while not model.equals(model_copy):
            model_copy = model.clone()
            model.accept(UnitTypeFixerVisitor())
            model.accept(ASTSymbolTableVisitor())
            model.accept(ASTParentVisitor())

    def _split_off_unit_type_term(self, unit_type, parent_unit_type: ASTUnitType, node):
        assert unit_type.is_simple_unit() or unit_type.is_pow or unit_type.is_arithmetic_expression()

        var_name = None

        if unit_type.is_pow:
            var_name = unit_type.base.unit

        if unit_type.is_simple_unit():
            var_name = unit_type.unit

        scope = node.get_scope()
        var_sym_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)
        if var_sym_resolve or unit_type.is_arithmetic_expression():
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
                expr_to_be_moved = var_simple_expr
            elif unit_type.is_arithmetic_expression():
                from pynestml.utils.model_parser import ModelParser
                expr_to_be_moved = ModelParser.parse_expression("(" + str(unit_type) + ")")
                # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                expr_to_be_moved.scope = node.scope
                expr_to_be_moved.source_position = node.source_position
                expr_to_be_moved.accept(ASTSymbolTableVisitor())
            else:
                raise Exception("Not implemented yet!")

            parent_node = ASTUtils.find_parent_node_by_type(node, ASTExpression)
            if parent_node:
                # appears inside an expression
                if parent_node.lhs == node:
                    if parent_node.get_binary_operator() and parent_unit_type.is_times:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                        new_node.source_position = parent_node.source_position
                        parent_node.lhs = new_node
                    elif parent_node.get_binary_operator() and parent_unit_type.is_div:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                        parent_node.lhs = new_node
                        new_node._parent = parent_node
                        new_node.source_position = parent_node.source_position
                    else:
                        raise Exception("not handled!")

                    return

                elif parent_node.rhs == node:
                    if parent_node.get_binary_operator() and parent_node.get_binary_operator().is_times_op and parent_unit_type.is_times:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=parent_node.lhs, rhs=new_numeric_literal_expr)
                        new_node.source_position = parent_node.source_position
                        parent_node.lhs = new_node
                        parent_node.rhs = expr_to_be_moved
                    elif parent_node.get_binary_operator() and parent_node.get_binary_operator().is_div_op and parent_unit_type.is_times:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=parent_node.lhs, rhs=new_numeric_literal_expr)
                        new_node.source_position = parent_node.source_position
                        parent_node.lhs = new_node
                        parent_node.binary_operator.is_div_op = False
                        parent_node.binary_operator.is_times_op = True
                        parent_node.rhs = expr_to_be_moved
                    elif parent_node.get_binary_operator() and parent_node.get_binary_operator().is_times_op and parent_unit_type.is_div:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=parent_node.lhs, rhs=new_numeric_literal_expr)
                        new_node.source_position = parent_node.source_position
                        parent_node.lhs = new_node
                        parent_node.binary_operator.is_div_op = True
                        parent_node.binary_operator.is_times_op = False
                        parent_node.rhs = expr_to_be_moved
                        new_node._parent = parent_node
                    elif parent_node.get_binary_operator() and parent_node.get_binary_operator().is_div_op and parent_unit_type.is_div:
                        binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                        new_node = ASTExpression(binary_operator=binary_operator, lhs=parent_node.lhs, rhs=new_numeric_literal_expr)
                        new_node.source_position = parent_node.source_position
                        parent_node.lhs = new_node
                        parent_node.rhs = expr_to_be_moved
                        new_node._parent = parent_node
                    else:
                        raise Exception("not handled!")

                    return
                else:
                    raise Exception("not handled!")

            parent_node = ASTUtils.find_parent_node_by_type(node, ASTAssignment)
            if parent_node:
                # appears on the rhs of an assignment

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
                new_node.source_position = parent_node.source_position

                return

            parent_node = ASTUtils.find_parent_node_by_type(node, ASTDeclaration)
            if parent_node:
                # appears on the rhs of a declaration

                if parent_unit_type.is_div:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                elif parent_unit_type.is_times:
                    binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                    new_node = ASTExpression(binary_operator=binary_operator, lhs=new_numeric_literal_expr, rhs=expr_to_be_moved)
                else:
                    raise Exception("not handled!")

                parent_node.expression = new_node
                new_node._parent = parent_node
                new_node.source_position = parent_node.source_position

                return

            raise Exception("not handled!")

    def visit_simple_expression(self, node: ASTSimpleExpression):
        if node.is_numeric_literal() and node.unitType:
            if node.unitType.is_times or node.unitType.is_div:
                if node.unitType.rhs.is_encapsulated:
                    self._split_off_unit_type_term(node.unitType.rhs.compound_unit, node.unitType, node)
                else:
                    self._split_off_unit_type_term(node.unitType.rhs, node.unitType, node)

                return
