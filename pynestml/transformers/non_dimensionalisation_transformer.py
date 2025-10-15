# -*- coding: utf-8 -*-
#
# non_dimensionalisation_transformer.py
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

from __future__ import annotations

from typing import Any, Dict, Sequence, Mapping, Optional, Union


from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.utils.logger import Logger, LoggingLevel
import astropy.units as u
import re


class NonDimVis(ASTVisitor):
    r"""
    Base class for non-dimensionalisation transformers.
    """

    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__()
        self.preferred_prefix = preferred_prefix

    PREFIX_FACTORS = {
        "Y": 1e24,      # yotta
        "Z": 1e21,      # zetta
        "E": 1e18,      # exa
        "P": 1e15,      # peta
        "T": 1e12,      # tera
        "G": 1e9,       # giga
        "M": 1e6,       # mega
        "k": 1e3,       # kilo
        "h": 1e2,       # hecto
        "da": 1e1,      # deca
        "": 1.0,        # no prefix
        "1": 1.0,       # no prefix
        "d": 1e-1,      # deci
        "c": 1e-2,      # centi
        "m": 1e-3,      # milli
        "u": 1e-6,      # micro (μ)
        "n": 1e-9,      # nano
        "p": 1e-12,     # pico
        "f": 1e-15,     # femto
        "a": 1e-18,     # atto
        "z": 1e-21,     # zepto
        "y": 1e-24,     # yocto
    }

    def get_conversion_factor_to_si(self, from_unit_str):
        r"""
        Return the conversion factor from the unit we have in the NESTML file to SI units.
        """

        from_unit = u.Unit(from_unit_str)
        scale = from_unit.si.scale

        return scale

    def _is_valid_astropy_unit(self, unit_string):
        """Check if a string can be interpreted as an astropy unit"""
        try:
            u.Unit(str(unit_string))
            return True
        except (ValueError, TypeError, u.UnitTypeError):
            return False


class NonDimensionalisationVarToRealTypeVisitor(NonDimVis):
    r"""
    Visitor changes the variable type on the LHS to "real".
    E.g.: My_declaration V = (30 * 1.0E-03) -> My_declaration real = (30 * 1.0E-03)
    Visitor has to be called last in the transformation process as the unit type information is used beforehand.
    """

    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)

    def visit_variable(self, node: ASTVariable):
        if not isinstance(node.get_type_symbol(), UnitTypeSymbol):
            return

        if Logger.logging_level.name == "DEBUG" or "INFO":
            print("The unit is: " + str(node.get_type_symbol().unit.unit))
            print(
                "The quantity is: "
                + str(node.get_type_symbol().unit.unit.physical_type)
            )

        parent_node = node.get_parent()
        new_node_type = RealTypeSymbol()
        new_variable = ASTVariable(
            name=node.name,
            type_symbol=node.get_type_symbol(),
            scope=node.get_scope(),
        )
        new_data_type = ASTDataType(
            is_real=True, type_symbol=new_node_type, scope=node.get_scope()
        )

        if isinstance(parent_node, ASTDeclaration):
            parent_node.variables[0] = new_variable
            parent_node.data_type = new_data_type
            pass

    def visit_input_port(self, node):
        if node.data_type is not None:
            new_node_type = RealTypeSymbol()
            new_data_type = ASTDataType(
                is_real=True, type_symbol=new_node_type, scope=node.get_scope()
            )
            parent_node = node.get_parent()
            for index, inputportexpression in enumerate(parent_node.input_definitions):
                if inputportexpression.name == node.name:
                    new_node = node.clone()
                    new_node.data_type = new_data_type
                    parent_node.input_definitions[index] = new_node

    def visit_inline_expression(self, node):
        if isinstance(node.data_type.type_symbol, RealTypeSymbol) or isinstance(
            node.data_type.type_symbol, UnitTypeSymbol
        ):
            if isinstance(node.data_type.type_symbol, RealTypeSymbol):
                if Logger.logging_level.name == "DEBUG" or "INFO":
                    print("\tReal number, no unit\n")

            elif isinstance(node.data_type.type_symbol, UnitTypeSymbol):
                if Logger.logging_level.name == "DEBUG" or "INFO":
                    print("The unit is: " + str(node.data_type.type_symbol.unit.unit))
                    print(
                        "The quantity is: "
                        + str(node.data_type.type_symbol.unit.unit.physical_type)
                    )

                parent_node = node.get_parent()
                new_node_type = RealTypeSymbol()
                new_data_type = ASTDataType(
                    is_real=True, type_symbol=new_node_type, scope=node.get_scope()
                )

                if isinstance(parent_node, ASTEquationsBlock):
                    for declaration in parent_node.declarations:
                        if isinstance(declaration, ASTInlineExpression):
                            if declaration.variable_name == node.variable_name:
                                declaration.data_type = new_data_type
        pass


class NonDimensionalisationPreferredPrefixFactorOnRhsVisitor(NonDimVis):
    r"""
    Visitor inserts the inverse value of the preferred prefix in scientific notation as a factor for the old encapsulated RHS expression for declarations and ODE equations.
    E.g.: V_m V = -70 * 1.0E-03, preferred prefix of mili for 'electric potential' -> V_m V = (1.0E+03 * (-70.0 * 1.0E-0.3))
    """

    def __init__(self, preferred_prefix: Dict[str, str], model):
        super().__init__(preferred_prefix)
        self.model = model

    def visit_declaration(self, node: ASTVariable) -> None:
        # get preferred prefix that declaring variable has
        if node.data_type.is_real:
            return

        if str(node.data_type.type_symbol.astropy_unit.physical_type) != "unknown":
            if node.variables[0].name == "__h":
                return

            for physical_type_string in self.preferred_prefix:
                if physical_type_string in str(node.data_type.type_symbol.astropy_unit.physical_type):
                    variable_physical_type_string = physical_type_string




            inverse_preferred_prefix_this_node_string = f"{1 / self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"

            # modify the node.expression to include the metric prefix as a factor in scientific notation on the lhs
            cloned_node = node.clone()
            lhs_expression = ASTSimpleExpression(
                numeric_literal=float(
                    inverse_preferred_prefix_this_node_string
                ),
                scope=node.get_scope(),
            )
            rhs_expression = node.expression
            new_sub_node = ASTExpression(
                is_encapsulated=False,
                binary_operator=ASTArithmeticOperator(is_times_op=True),
                lhs=lhs_expression,
                rhs=rhs_expression,
                scope=node.get_scope(),
            )
            cloned_node.expression = ASTExpression(
                is_encapsulated=True,
                expression=new_sub_node,
                scope=node.get_scope(),
            )

            for declaration in node.get_parent().declarations:
                if declaration.variables[0].name == node.variables[0].name:
                    declaration.expression = cloned_node.expression

    @staticmethod
    def _derivate_regex(var_names: list) -> re:
        pattern = rf"^({'|'.join(map(re.escape, var_names))})('+)?$"
        return re.compile(pattern)

    def visit_ode_equation(self, node: ASTOdeEquation):
        # insert preferred prefix conversion factor for LHS on rhs
        var_names = [
            str(obj)
            for obj in ASTUtils.all_variables_defined_in_block(
                self.model.get_state_blocks() + self.model.get_parameters_blocks()
            )
        ]
        regex = self._derivate_regex(var_names)
        corresponding_non_diff_variable = regex.match(node.lhs.name).group()
        if hasattr(
            ASTUtils.get_variable_by_name(
                self.model, corresponding_non_diff_variable
            ).type_symbol,
            "astropy_unit",
        ):
            corresponding_non_diff_variable_physical_type_string = str(
                ASTUtils.get_variable_by_name(
                    self.model, corresponding_non_diff_variable
                ).type_symbol.astropy_unit.physical_type
            )
            inverse_preferred_prefix_this_node_string = f"{1e-3 * 1 / self.PREFIX_FACTORS[self.preferred_prefix[corresponding_non_diff_variable_physical_type_string]]:.1E}"
            cloned_node = node.clone()
            lhs_expression = ASTSimpleExpression(
                numeric_literal=float(inverse_preferred_prefix_this_node_string),
                scope=node.get_scope(),
            )
            rhs_expression = ASTExpression(is_encapsulated=True, expression=node.rhs)
            new_sub_node = ASTExpression(
                is_encapsulated=False,
                binary_operator=ASTArithmeticOperator(is_times_op=True),
                lhs=lhs_expression,
                rhs=rhs_expression,
                scope=node.get_scope(),
            )
            cloned_node.rhs = ASTExpression(
                is_encapsulated=True, expression=new_sub_node, scope=node.get_scope()
            )
            for declaration in node.get_parent().declarations:
                if isinstance(declaration, ASTOdeEquation):
                    if declaration.lhs.name == node.lhs.name:
                        declaration.rhs.type = RealTypeSymbol()
                        declaration.rhs = cloned_node.rhs
            return

    def visit_assignment(self, node):
        # insert reciprocal of preferred prefix on RHS
        for state_declaration in self.model.get_state_blocks()[0].declarations:
            if (
                state_declaration.variables[0].name
                == node.lhs.name
            ):
                if not isinstance(
                    state_declaration.variables[0].type_symbol, RealTypeSymbol
                ):
                    corresponding_physical_type_string = str(
                        state_declaration.variables[
                            0
                        ].type_symbol.astropy_unit.physical_type
                    )
                    inverse_preferred_prefix_this_node_string = f"{1 / self.PREFIX_FACTORS[self.preferred_prefix[corresponding_physical_type_string]]:.1E}"
                    cloned_parent_node = node.get_parent()
                    lhs_expression = ASTSimpleExpression(
                        numeric_literal=float(
                            inverse_preferred_prefix_this_node_string
                        ),
                        scope=node.get_scope(),
                    )
                    rhs_expression = ASTExpression(
                        is_encapsulated=True,
                        expression=node.stmts_body.stmts[
                            0
                        ].small_stmt.assignment.rhs,
                    )
                    new_sub_node = ASTExpression(
                        is_encapsulated=False,
                        binary_operator=ASTArithmeticOperator(is_times_op=True),
                        lhs=lhs_expression,
                        rhs=rhs_expression,
                        scope=node.get_scope(),
                    )
                    cloned_node.stmts_body.stmts[
                        0
                    ].small_stmt.assignment.rhs = ASTExpression(
                        is_encapsulated=True,
                        expression=new_sub_node,
                        scope=node.get_scope(),
                    )
                    assignment = node.stmts_body.stmts[0].small_stmt.assignment
                    inverse_value = float(inverse_preferred_prefix_this_node_string)

                    new_rhs = ASTExpression(
                        is_encapsulated=True,
                        expression=ASTExpression(
                            is_encapsulated=False,
                            binary_operator=ASTArithmeticOperator(is_times_op=True),
                            lhs=ASTSimpleExpression(
                                numeric_literal=inverse_value,
                                scope=node.get_scope(),
                            ),
                            rhs=ASTExpression(
                                is_encapsulated=True,
                                expression=assignment.rhs,
                                scope=node.get_scope(),
                            ),
                            scope=node.get_scope(),
                        ),
                        scope=node.get_scope(),
                    )
                    assignment.rhs = new_rhs


    # def visit_on_receive_block(self, node):
    #     # insert reciprocal of preferred prefix on RHS
    #     if isinstance(node.stmts_body.stmts[0].small_stmt.assignment, ASTAssignment):
    #         for state_declaration in self.model.get_state_blocks()[0].declarations:
    #             if (
    #                 state_declaration.variables[0].name
    #                 == node.stmts_body.stmts[0].small_stmt.assignment.lhs.name
    #             ):
    #                 if not isinstance(
    #                     state_declaration.variables[0].type_symbol, RealTypeSymbol
    #                 ):
    #                     corresponding_physical_type_string = str(
    #                         state_declaration.variables[
    #                             0
    #                         ].type_symbol.astropy_unit.physical_type
    #                     )
    #                     inverse_preferred_prefix_this_node_string = f"{1 / self.PREFIX_FACTORS[self.preferred_prefix[corresponding_physical_type_string]]:.1E}"
    #                     cloned_node = node.clone()
    #                     lhs_expression = ASTSimpleExpression(
    #                         numeric_literal=float(
    #                             inverse_preferred_prefix_this_node_string
    #                         ),
    #                         scope=node.get_scope(),
    #                     )
    #                     rhs_expression = ASTExpression(
    #                         is_encapsulated=True,
    #                         expression=node.stmts_body.stmts[
    #                             0
    #                         ].small_stmt.assignment.rhs,
    #                     )
    #                     new_sub_node = ASTExpression(
    #                         is_encapsulated=False,
    #                         binary_operator=ASTArithmeticOperator(is_times_op=True),
    #                         lhs=lhs_expression,
    #                         rhs=rhs_expression,
    #                         scope=node.get_scope(),
    #                     )
    #                     cloned_node.stmts_body.stmts[
    #                         0
    #                     ].small_stmt.assignment.rhs = ASTExpression(
    #                         is_encapsulated=True,
    #                         expression=new_sub_node,
    #                         scope=node.get_scope(),
    #                     )
    #                     assignment = node.stmts_body.stmts[0].small_stmt.assignment
    #                     inverse_value = float(inverse_preferred_prefix_this_node_string)

    #                     new_rhs = ASTExpression(
    #                         is_encapsulated=True,
    #                         expression=ASTExpression(
    #                             is_encapsulated=False,
    #                             binary_operator=ASTArithmeticOperator(is_times_op=True),
    #                             lhs=ASTSimpleExpression(
    #                                 numeric_literal=inverse_value,
    #                                 scope=node.get_scope(),
    #                             ),
    #                             rhs=ASTExpression(
    #                                 is_encapsulated=True,
    #                                 expression=assignment.rhs,
    #                                 scope=node.get_scope(),
    #                             ),
    #                             scope=node.get_scope(),
    #                         ),
    #                         scope=node.get_scope(),
    #                     )
    #                     assignment.rhs = new_rhs

    def visit_inline_expression(self, node):
        if not node.data_type.is_real:
            if str(node.data_type.type_symbol.astropy_unit.physical_type) != "unknown":
                for physical_type_string in self.preferred_prefix:
                    if physical_type_string in str(
                        node.data_type.type_symbol.astropy_unit.physical_type
                    ):
                        variable_physical_type_string = physical_type_string
                inverse_preferred_prefix_this_node_string = f"{1 / self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"
                # modify the node.expression to include the metric prefix as a factor in scientific notation on the lhs
                cloned_node = node.clone()
                lhs_expression = ASTSimpleExpression(
                    numeric_literal=float(inverse_preferred_prefix_this_node_string),
                    scope=node.get_scope(),
                )
                rhs_expression = node.expression
                new_sub_node = ASTExpression(
                    is_encapsulated=False,
                    binary_operator=ASTArithmeticOperator(is_times_op=True),
                    lhs=lhs_expression,
                    rhs=rhs_expression,
                    scope=node.get_scope(),
                )
                cloned_node.expression = ASTExpression(
                    is_encapsulated=True,
                    expression=new_sub_node,
                    scope=node.get_scope(),
                )

                for declaration in node.get_parent().declarations:
                    if hasattr(declaration, "variable_name"):
                        if declaration.variable_name == node.variable_name:
                            declaration.expression = cloned_node.expression

class NonDimensionalisationRHSVariableVisitor(NonDimVis):
    r"""
    Visitor inserts the inverse value of the preferred prefix in scientific notation as a factor for the old encapsulated RHS expression for declarations and ODE equations.
    E.g.: V_m V = -70 * 1.0E-03, preferred prefix of mili for 'electric potential' -> V_m V = (1.0E+03 * (-70.0 * 1.0E-0.3))
    """

    def __init__(self, preferred_prefix: Dict[str, str], model):
        super().__init__(preferred_prefix)
        self.model = model

    def visit_declaration(self, node: ASTDeclaration) -> None:
        print("Visit decl " + str(node))
        node.get_expression().accept(NonDimensionalisationVariableVisitor(self.preferred_prefix))

    def visit_ode_equation(self, node: ASTOdeEquation):
        node.get_rhs().accept(NonDimensionalisationVariableVisitor(self.preferred_prefix))

    def visit_inline_expression(self, node: ASTInlineExpression):
        node.get_expression().accept(NonDimensionalisationVariableVisitor(self.preferred_prefix))

    def visit_assignment(self, node: ASTAssignment):
        node.get_expression().accept(NonDimensionalisationVariableVisitor(self.preferred_prefix))



class NonDimensionalisationNumericLiteralVisitor(NonDimVis):
    r"""
    Visitor changes unit symbols and numeric prefixes to numerical factors in epxressions on RHSs, where the numerical prefix and unit are positioned after an expression
    E.g.: Var_a V = .... + (4 + 3) * mV -> Var_a V = .... + ((4 + 3) * 1.0E-03)
    """

    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)

    def visit_variable(self, node: ASTVariable) -> None:
        if not hasattr(node.get_parent(), "variable"):
            return

        symbol_is_defined_as_a_variable: bool = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
        if symbol_is_defined_as_a_variable or (not super()._is_valid_astropy_unit(node.name)):
            return

        if (node.get_parent().variable.name != node.get_name()
            or node.get_parent().numeric_literal is None
        ):
            return

        # The variable encountered is something like mV, without a numeric literal in front, e.g. (4 + 3) * mV
        assert PredefinedUnits.is_unit(node.get_name())
        conversion_factor = float(f"{super().get_conversion_factor_to_si(node.get_name()):.1E}")

        if conversion_factor == 1:
            # skip conversation with factor 1
            return

        parent_node = node.get_parent()
        assert isinstance(parent_node, ASTSimpleExpression), "Don't know how to handle ASTVariable that is not inside an ASTSimpleExpression"

        parent_node.set_numeric_literal(conversion_factor * parent_node.get_numeric_literal())
        parent_node.set_variable(None)


class NonDimensionalisationVariableVisitor(NonDimVis):
    r"""
    Visitor changes variables from their preferred prefix into an SI prefix, e.g. "V_m" --> "1E-3 * V_m"
    """

    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)

    def visit_variable(self, node: ASTVariable) -> None:
        print("NonDimensionalisationVariableVisitor: visit_variable(" + str(node))
        if node.get_type_symbol():
            type_sym = node.get_type_symbol()
        else:
            var_sym = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
            type_sym = var_sym.type_symbol

        var_unit = type_sym.unit.unit
        var_quantity = var_unit.physical_type
        var_preferred_prefix = self.preferred_prefix[str(var_quantity)]
        conversion_factor_to_si = float(self.PREFIX_FACTORS[var_preferred_prefix])

        # multiply the variable by conversion_factor_to_si
        parent_node = node.get_parent()

        assert isinstance(parent_node, ASTSimpleExpression), "Don't know how to handle ASTVariable that is not inside an ASTSimpleExpression"



        lhs_expression = ASTSimpleExpression(
                numeric_literal=conversion_factor_to_si,
                scope=node.get_scope(),
            )
        rhs_expression = ASTSimpleExpression(
                variable=node,
                scope=node.get_scope(),
            )
        new_sub_node = ASTExpression(
            is_encapsulated=False,
            binary_operator=ASTArithmeticOperator(is_times_op=True),
            lhs=lhs_expression,
            rhs=rhs_expression,
            scope=node.get_scope(),
        )
        new_node = ASTExpression(
            is_encapsulated=True,
            expression=new_sub_node,
            scope=node.get_scope()
        )

        grandparent_node = parent_node.get_parent()
        if isinstance(grandparent_node, ASTDeclaration):
            # something of the form: ``V_m mV = E_L``
            # change it into ``V_m mv = conversion_factor_to_si * E_L``

            grandparent_node.set_expression(new_sub_node)
        elif isinstance(grandparent_node, ASTExpression) and grandparent_node.get_binary_operator() is not None and grandparent_node.get_binary_operator().is_times_op:
            # of the form "1000 * V_m" or "V_m * foo"

            if grandparent_node.rhs == parent_node:
                grandparent_node.rhs = new_node
            else:
                assert grandparent_node.lhs == parent_node
                grandparent_node.lhs = new_node
        else:
            raise Exception("Don't know how to handle grandparent node type: " + str(type(grandparent_node)))


class NonDimensionalisationSimpleExpressionVisitor(NonDimVis):
    r"""
    Visitor converts unit-ful simple expressions with metric prefixes to real type expressions in the corresponding SI base unit in RHSs.
    E.g.:

    .. code:: NESTML

       Var_a V = ...... * 3 MV

    becomes

    .. code:: NESTML

       Var_a V = ...... * (3 * 1.0E+06)
    """

    def __init__(self, preferred_prefix: Dict[str, str], model):
        super().__init__(preferred_prefix)
        self.model = model

    def _handle_node(self, node):
        if hasattr(node, "variable"):
            if str(node.variable) == "spikes":
                return  # spikes have 1/s in NESTML

        if node.get_numeric_literal() is not None:
            print("Numeric literal: " + str(node.get_numeric_literal()))
            if isinstance(node.type, RealTypeSymbol):
                print("\tReal number, no unit\n")
                return
            elif isinstance(node.type, UnitTypeSymbol):
                # the expression 3 MV is a SimpleExpression for example
                parent_node = node.get_parent()
                print("\tUnit: " + str(node.type.unit.unit))
                conversion_factor = (
                    f"{super().get_conversion_factor_to_si(node.variable.name):.1E}"
                )
                numeric_literal = node.get_numeric_literal()
                lhs_expression = ASTSimpleExpression(
                    numeric_literal=float(numeric_literal), scope=node.get_scope()
                )
                rhs_expression = ASTSimpleExpression(
                    numeric_literal=float(str(conversion_factor)),
                    scope=node.get_scope(),
                )
                if isinstance(parent_node, ASTExpression):
                    new_sub_node = ASTExpression(
                        is_encapsulated=False,
                        binary_operator=ASTArithmeticOperator(is_times_op=True),
                        lhs=lhs_expression,
                        rhs=rhs_expression,
                        scope=node.get_scope(),
                    )
                    new_node = ASTExpression(
                        is_encapsulated=True,
                        expression=new_sub_node,
                        scope=node.get_scope(),
                        unary_operator=parent_node.unary_operator,
                    )
                    if parent_node.binary_operator is not None:
                        parent_node.binary_operator = parent_node.binary_operator
                        if parent_node.rhs == node:
                            parent_node.rhs = new_node
                        elif parent_node.lhs == node:
                            parent_node.lhs = new_node
                        else:
                            raise Exception(
                                "Node is neither lhs nor rhs of parent, possibly expression - should not execute until here."
                            )
                    elif parent_node.binary_operator is None:
                        parent_node.rhs = None
                        parent_node.expression = new_node
                        parent_node.unary_operator = None
                    else:
                        raise Exception("This case is also possible and needs handling")
                if isinstance(parent_node, ASTDeclaration):
                    new_sub_node = ASTExpression(
                        is_encapsulated=False,
                        binary_operator=ASTArithmeticOperator(is_times_op=True),
                        lhs=lhs_expression,
                        rhs=rhs_expression,
                        scope=node.get_scope(),
                    )
                    new_node = ASTExpression(
                        is_encapsulated=True,
                        expression=new_sub_node,
                        scope=node.get_scope(),
                    )
                    parent_node.expression = new_node

            elif isinstance(node.type, IntegerTypeSymbol):
                print("\tInteger type number, no unit\n")
            else:
                raise Exception(
                    "Node type is neither RealTypeSymbol nor UnitTypeSymbol"
                )
            return

        if node.function_call is None:
            if isinstance(node.get_parent(), ASTFunctionCall) and node.get_parent().get_name() in [PredefinedFunctions.INTEGRATE_ODES, PredefinedFunctions.CONVOLVE, PredefinedFunctions.DELTA, PredefinedFunctions.TIME_STEPS, PredefinedFunctions.EMIT_SPIKE]:
                # skip certain predefined functions, e.g. don't add factors to "integrate_odes(V_m)" call
                return

            if node.get_numeric_literal() is None:
                # get physical type of node
                if isinstance(node.type, UnitTypeSymbol):
                    if "spikes" not in node.variable.name:
                        symbol_is_defined_as_a_variable: bool = node.variable.get_scope().resolve_to_symbol(node.variable.get_complete_name(), SymbolKind.VARIABLE) is not None
                        if ((not symbol_is_defined_as_a_variable)
                            and super()._is_valid_astropy_unit(node.variable.name)
                            and (node.get_parent().binary_operator is not None
                                 or node.get_parent().unary_operator is not None)):
                            # This should be handled by visit_variable instead - return early
                            return
                        else:
                            if str(node.type.astropy_unit.physical_type) != "unknown":
                                variable_physical_type_string = "error"
                                for physical_type_string in self.preferred_prefix:
                                    if physical_type_string in str(
                                        node.type.astropy_unit.physical_type
                                    ):
                                        variable_physical_type_string = (
                                            physical_type_string
                                        )
                                # get preferred prefix for this node
                                if variable_physical_type_string == "error":
                                    raise Exception("AstroPy Physical Type \"" + str(node.type.astropy_unit.physical_type) + "\" could not be determined. Is it really defined in preferred prefixes?")
                                preferred_prefix_this_node_string = f"{self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"
                                # create a new sub node that multiplies the variable with the reciprocal of the preferred prefix
                                lhs_expression = node.clone()
                                rhs_expression = ASTSimpleExpression(
                                    numeric_literal=float(
                                        preferred_prefix_this_node_string
                                    ),
                                    scope=node.get_scope(),
                                )
                                new_sub_node = ASTExpression(
                                    is_encapsulated=False,
                                    binary_operator=ASTArithmeticOperator(
                                        is_times_op=True
                                    ),
                                    lhs=lhs_expression,
                                    rhs=rhs_expression,
                                    scope=node.get_scope(),
                                )
                                parent_node = node.get_parent()
                                if hasattr(parent_node, "unary_operator"):
                                    # create new node encapsulating multiplication
                                    new_node = ASTExpression(
                                        is_encapsulated=True,
                                        expression=new_sub_node,
                                        scope=node.get_scope(),
                                        unary_operator=parent_node.unary_operator,
                                    )
                                    # attach new node to parent node
                                    grandparent_node = parent_node.get_parent()
                                    if any(
                                        hasattr(parent_node, attr)
                                        for attr in ["lhs", "rhs"]
                                    ):
                                        if node == parent_node.lhs:
                                            if parent_node.binary_operator is not None:
                                                parent_node.binary_operator = (
                                                    parent_node.binary_operator
                                                )
                                                parent_node.lhs = new_node
                                                parent_node.rhs = parent_node.rhs
                                                return
                                            elif parent_node.binary_operator is None:
                                                parent_node.rhs = None
                                                parent_node.expression = new_node
                                                parent_node.unary_operator = None
                                                return
                                        if node == parent_node.rhs:
                                            if parent_node.binary_operator is not None:
                                                parent_node.binary_operator = (
                                                    parent_node.binary_operator
                                                )
                                                parent_node.rhs = new_node
                                                parent_node.lhs = parent_node.lhs
                                                return
                                            elif parent_node.binary_operator is None:
                                                parent_node.rhs = None
                                                parent_node.expression = new_node
                                                parent_node.unary_operator = None
                                                return
                                        if parent_node == grandparent_node.lhs:
                                            grandparent_node.lhs = new_node
                                            return
                                        if parent_node == parent_node.rhs:
                                            grandparent_node.rhs = new_node
                                            return
                                    elif parent_node == parent_node.expression:
                                        parent_node.expression = new_node
                                        return
                                    else:
                                        raise Exception(
                                            "Parent node has no attribute lhs, rhs or expression."
                                        )
                                elif not (hasattr(parent_node, "unary_operator")):
                                    # create new node encapsulating multiplication
                                    new_node = ASTExpression(
                                        is_encapsulated=True,
                                        expression=new_sub_node,
                                        scope=node.get_scope(),
                                    )
                                    # attach new node to parent node
                                    if any(
                                        hasattr(parent_node, attr)
                                        for attr in ["lhs", "rhs"]
                                    ):
                                        if node == parent_node.lhs:
                                            if parent_node.binary_operator is not None:
                                                parent_node.binary_operator = (
                                                    parent_node.binary_operator
                                                )
                                                parent_node.lhs = new_node
                                                parent_node.rhs = parent_node.rhs
                                                return
                                            elif parent_node.binary_operator is None:
                                                parent_node.rhs = None
                                                parent_node.expression = new_node
                                                parent_node.unary_operator = None
                                                return
                                        if node == parent_node.rhs:
                                            if not hasattr(node, "binary_operator"):
                                                parent_node.expression = new_node
                                                return
                                            elif (
                                                parent_node.binary_operator is not None
                                            ):
                                                parent_node.binary_operator = (
                                                    parent_node.binary_operator
                                                )
                                                parent_node.rhs = new_node
                                                parent_node.lhs = parent_node.lhs
                                                return
                                            elif parent_node.binary_operator is None:
                                                parent_node.rhs = None
                                                parent_node.expression = new_node
                                                parent_node.unary_operator = None
                                                return
                                    elif hasattr(parent_node, "expression"):
                                        parent_node.args = new_node
                                        return
                                    elif hasattr(parent_node, "args"):
                                        for i, arg in enumerate(parent_node.args):
                                            if node == arg:
                                                parent_node.args[i] = new_node
                                                return
                                        raise Exception("arg not found in parent node arguments list")
                                    else:
                                        raise Exception("Parent node has no rhs or lhs.")

    def visit_simple_expression(self, node):
        # if node.function_call is not None:
        #     print("Function call")
        #     for arg in node.function_call.get_args():
        #         self.visit(arg)

        #     import pdb;pdb.set_trace()


        # else:
        self._handle_node(node)

        super().visit_simple_expression(node)


class NonDimensionalisationTransformer(Transformer):
    r"""Remove all units from the model and replace them with real type.

    The transformer relates to [PR-1217](https://github.com/nest/nestml/pull/1217) and [Issue-984](https://github.com/nest/nestml/issues/984).

    The correct transformation of the expressions inside a NESTML file should be checked. The tests should include:
    - checking for all metric prefixes
    - checking for nested expressions with metric prefixes
    - checking that transformations occur in every part of the NESTML file units are specified
    - checking of transformation for derived variables
    - checking for transformation of reciprocal units/ expressions with reciprocal units
    - does it make sense for these to have the same desired unit?
    - E.g.: desired unit of 'electrical potential' is mV -> should variables with physical type of '1/V' also be then expressed as '1/mV' post transformation?
    - see *test_reciprocal_unit_in_paramterblock*
    - checking additional parenthesis are set correctly

    In a second instance the unit arithmetic and consistency of physical types needs to be checked pre-transformation after the original AST is built:
    - will the expression on the RHS of an equation yield a unit that is a unit of what is specified on the LHS of the equation?
    - How should exceptions be handled, for example if LHS is 'V' but result on RHS is '1/V'?
    - Are the arguments inside of functions like exp(), log(), sin(), etc. dimensionless or has the user made a mistake?
    - What should happen if unknown units are encountered?

    These tests can be found in ``tests/nest_tests/non_dimensionalisation_transformer``.
    """

    _default_options = {
        "quantity_to_preferred_prefix": {},
        "variable_to_preferred_prefix": {},
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform_(
        self, model: Union[ASTNode, Sequence[ASTNode]]
    ) -> Union[ASTNode, Sequence[ASTNode]]:
        transformed_model = model.clone()
        transformed_model.accept(ASTParentVisitor())
        transformed_model.accept(ASTSymbolTableVisitor())

        literal_visitor = NonDimensionalisationNumericLiteralVisitor(
            self.get_option("quantity_to_preferred_prefix")
        )
        simple_expression_visitor = NonDimensionalisationSimpleExpressionVisitor(
            self.get_option("quantity_to_preferred_prefix"), model
        )
        rhs_preferred_prefix_visitor = NonDimensionalisationPreferredPrefixFactorOnRhsVisitor(
            self.get_option("quantity_to_preferred_prefix"), model
        )
        var_to_real_type_visitor = NonDimensionalisationVarToRealTypeVisitor(
            self.get_option("quantity_to_preferred_prefix")
        )
        rhs_variable_visitor = NonDimensionalisationRHSVariableVisitor(
            self.get_option("quantity_to_preferred_prefix"), model
        )

        transformed_model.accept(ASTParentVisitor())
        transformed_model.accept(literal_visitor)

        if Logger.logging_level.name == "DEBUG":
            print("NonDimensionalisationTransformer(): model after literal visitor:")
            print(transformed_model)

        transformed_model.accept(rhs_variable_visitor)

        if Logger.logging_level.name == "DEBUG":
            print("NonDimensionalisationTransformer(): model after variable visitor:")
            print(transformed_model)


        # transformed_model.accept(simple_expression_visitor)
        transformed_model.accept(rhs_preferred_prefix_visitor)

        if Logger.logging_level.name == "DEBUG":
            print("NonDimensionalisationTransformer(): model after rhs_preferred_prefix_visitor visitor:")
            print(transformed_model)


        transformed_model.accept(var_to_real_type_visitor)

        if Logger.logging_level.name == "DEBUG":
            print("NonDimensionalisationTransformer(): model after var_to_real_type_visitor visitor:")
            print(transformed_model)


        transformed_model.accept(ASTParentVisitor())
        transformed_model.accept(ASTSymbolTableVisitor())
        # if Logger.logging_level.name == "DEBUG":
        #     print("NonDimensionalisationTransformer(): model after transformation:")
        #     print(transformed_model)

        return transformed_model

    def transform(
        self, models: Union[ASTNode, Sequence[ASTNode]]
    ) -> Union[ASTNode, Sequence[ASTNode]]:
        transformed_models = []

        single = False
        if isinstance(models, ASTNode):
            single = True
            model = [models]

        for model in models:
            transformed_models.append(self.transform_(model))

        if single:
            return transformed_models[0]

        return transformed_models
