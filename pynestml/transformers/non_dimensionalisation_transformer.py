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

from quantities.quantity import get_conversion_factor
from scipy.stats import reciprocal

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
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
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
import astropy.units as u
import re

class NonDimVis(ASTVisitor):
    r"""
    Base class for non-dimensionalisation transformers.
    """
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__()
        self.preferred_prefix = preferred_prefix
        # self.variable_original_metric_prefix_dict = dict()

    PREFIX_FACTORS = {
        'Y': 1e24,   # yotta
        'Z': 1e21,   # zetta
        'E': 1e18,   # exa
        'P': 1e15,   # peta
        'T': 1e12,   # tera
        'G': 1e9,    # giga
        'M': 1e6,    # mega
        'k': 1e3,    # kilo
        'h': 1e2,    # hecto
        'da': 1e1,   # deca
        '': 1.0,     # no prefix
        '1': 1.0,    # no prefix
        'd': 1e-1,   # deci
        'c': 1e-2,   # centi
        'm': 1e-3,   # milli
        'u': 1e-6,   # micro (μ)
        'n': 1e-9,   # nano
        'p': 1e-12,  # pico
        'f': 1e-15,  # femto
        'a': 1e-18,  # atto
        'z': 1e-21,  # zepto
        'y': 1e-24,  # yocto
    }

    def get_conversion_factor_to_si(self, from_unit_str):
        r"""
        Return the conversion factor from the unit we have in the NESTML file to SI units.
        """

        from_unit = u.Unit(from_unit_str)
        scale = from_unit.si.scale

        return scale

class NonDimensionalisationVarToRealTypeVisitor(NonDimVis):
    r"""
    This visitor changes the variable type on the LHS to "real"
    E.g.: My_declaration V = (30 * 1.0E-03) -> My_declaration real = (30 * 1.0E-03)
    This visitor has to be called last in the transformation process as the unit type information is needed before
    """
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)

    def visit_variable(self, node: ASTVariable):
        if (isinstance(node.get_type_symbol(), RealTypeSymbol) or isinstance(node.get_type_symbol(), UnitTypeSymbol)):
            if(isinstance(node.get_type_symbol(), RealTypeSymbol)):
                print("\tReal number, no unit\n")
            elif (isinstance(node.get_type_symbol(), UnitTypeSymbol)):
                print("The unit is: "+str(node.get_type_symbol().unit.unit))
                print("The quantity is: "+str(node.get_type_symbol().unit.unit.physical_type))

                parent_node = node.get_parent()
                new_node_type = RealTypeSymbol()
                new_variable = ASTVariable(name=node.name, type_symbol=node.get_type_symbol(), scope=node.get_scope())
                new_data_type = ASTDataType(is_real=True, type_symbol=new_node_type, scope=node.get_scope())

                if isinstance(parent_node, ASTDeclaration):
                    parent_node.variables[0] = new_variable
                    parent_node.data_type = new_data_type
                    pass


    def visit_inline_expression(self, node):
        # return super().visit_inline_expression(node)
        if (isinstance(node.data_type.type_symbol, RealTypeSymbol) or isinstance(node.data_type.type_symbol, UnitTypeSymbol)):
            if(isinstance(node.data_type.type_symbol, RealTypeSymbol)):
                print("\tReal number, no unit\n")
            elif (isinstance(node.data_type.type_symbol, UnitTypeSymbol)):
                print("The unit is: "+str(node.data_type.type_symbol.unit.unit))
                print("The quantity is: "+str(node.data_type.type_symbol.unit.unit.physical_type))

                parent_node = node.get_parent()
                new_node_type = RealTypeSymbol()
                # new_variable = ASTVariable(name=node.name, type_symbol=node.get_type_symbol(), scope=node.get_scope())
                new_data_type = ASTDataType(is_real=True, type_symbol=new_node_type, scope=node.get_scope())

                if isinstance(parent_node, ASTEquationsBlock):
                    for declaration in parent_node.declarations:
                        if declaration.variable_name == node.variable_name:
                            declaration.data_type = new_data_type
        pass
        



class NonDimensionalisationPreferredPrefixFactorOnRhsVisitor(NonDimVis):
    r"""
    This visitor inserts the inverse value of the preferred prefix in scientific notation as a factor for the old encapsulated RHS expression for declarations and ODE equations
    E.g.: V_m V = -70 * 1.0E-03, preferred prefix of mili for 'electric potential' -> V_m V = (1.0E+03 * (-70.0 * 1.0E-0.3))
    """
    def __init__(self, preferred_prefix: Dict[str, str], model):
        super().__init__(preferred_prefix)
        self.model = model

    def visit_declaration(self, node: ASTVariable) -> None:

        # get preferred prefix that declaring variable has
        if not node.data_type.is_real:
            if str(node.data_type.type_symbol.astropy_unit.physical_type) != "unknown":
                if node.variables[0].name != "__h":
                    for physical_type_string in self.preferred_prefix:
                        if physical_type_string in str(node.data_type.type_symbol.astropy_unit.physical_type):
                            variable_physical_type_string = physical_type_string
                    # variable_physical_type_string = str(node.data_type.type_symbol.astropy_unit.physical_type)
                    inverse_preferred_prefix_this_node_string = f"{1/self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"
                    # modify the node.expression to include the metric prefix as a factor in scientific notation on the lhs
                    cloned_node = node.clone()
                    lhs_expression = ASTSimpleExpression(string=inverse_preferred_prefix_this_node_string, scope=node.get_scope())
                    rhs_expression = node.expression
                    new_sub_node = ASTExpression(is_encapsulated=False,
                                                 binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                 lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                    cloned_node.expression = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())


                    for declaration in node.get_parent().declarations:
                        if declaration.variables[0].name == node.variables[0].name:
                            declaration.expression = cloned_node.expression
        pass


    @staticmethod
    def _derivate_regex(var_names:list)->re:
        # escaped = map(re.escape, var_names)
        pattern = rf"^({'|'.join(map(re.escape, var_names))})('+)?$"
        return re.compile(pattern)

    def visit_ode_equation(self, node: ASTOdeEquation):
        # insert preferred prefix conversion factor for LHS on rhs
        var_names = [str(obj) for obj in ASTUtils.all_variables_defined_in_block(self.model.get_state_blocks()+self.model.get_parameters_blocks())]
        regex = self._derivate_regex(var_names)
        corresponding_non_diff_variable = regex.match(node.lhs.name).group()
        corresponding_non_diff_variable_physical_type_string = str(ASTUtils.get_variable_by_name(self.model, corresponding_non_diff_variable).type_symbol.astropy_unit.physical_type)
        inverse_preferred_prefix_this_node_string = f"{(1.0E-3)*1/self.PREFIX_FACTORS[self.preferred_prefix[corresponding_non_diff_variable_physical_type_string]]:.1E}"
        # inverse_preferred_prefix_this_node_string = f"{1:.1E}"
        cloned_node = node.clone()
        lhs_expression = ASTSimpleExpression(string=inverse_preferred_prefix_this_node_string, scope=node.get_scope())
        rhs_expression = ASTExpression(is_encapsulated=True, expression=node.rhs)
        new_sub_node = ASTExpression(is_encapsulated=False,
                                     binary_operator=ASTArithmeticOperator(is_times_op=True),
                                     lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
        cloned_node.rhs = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())
        for declaration in node.get_parent().declarations:
            if declaration.lhs.name == node.lhs.name:
                declaration.rhs = cloned_node.rhs
        pass

    def visit_inline_expression(self, node):
        if not node.data_type.is_real:
            if str(node.data_type.type_symbol.astropy_unit.physical_type) != "unknown":
                for physical_type_string in self.preferred_prefix:
                    if physical_type_string in str(node.data_type.type_symbol.astropy_unit.physical_type):
                        variable_physical_type_string = physical_type_string
                # variable_physical_type_string = str(node.data_type.type_symbol.astropy_unit.physical_type)
                inverse_preferred_prefix_this_node_string = f"{1/self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"
                # modify the node.expression to include the metric prefix as a factor in scientific notation on the lhs
                cloned_node = node.clone()
                lhs_expression = ASTSimpleExpression(string=inverse_preferred_prefix_this_node_string, scope=node.get_scope())
                rhs_expression = node.expression
                new_sub_node = ASTExpression(is_encapsulated=False,
                                                binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                cloned_node.expression = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())
                pass
                for declaration in node.get_parent().declarations:
                    if declaration.variable_name == node.variable_name:
                        declaration.expression = cloned_node.expression
        # return super().visit_inline_expression(node)
        pass


class NonDimensionalisationVariableVisitor(NonDimVis):
    r"""
    This visitor changes unit symbols and numeric prefixes to numerical factors in epxressions on RHSs, where the numerical prefix and unit are positioned after an expression
    E.g.: Var_a V = .... + (4 + 3) * mV -> Var_a V = .... + ((4 + 3) * 1.0E-03)
    """
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)

    def visit_variable(self, node: ASTVariable) -> None:
        if not ((isinstance(node.get_type_symbol(), RealTypeSymbol)) or (isinstance(node.get_type_symbol(), UnitTypeSymbol)) or (node.get_type_symbol() is None)):
            if (isinstance(node, ASTVariable) and node.get_parent().variable.name == node.get_name() and node.get_parent().numeric_literal == None):
                # Then the variable encountered is something like mV, without a numeric literal in front, e.g. (4 + 3) * mV
                conversion_factor = f"{super().get_conversion_factor_to_si(node.get_name()):.1E}"
                parent_node = node.get_parent()
                grandparent_node = parent_node.get_parent()
                rhs_expression = ASTSimpleExpression(string=str(conversion_factor), scope=node.get_scope())
                if grandparent_node.binary_operator is not None:
                    grandparent_node.rhs = rhs_expression
                pass
        else:
            pass
            # raise Exception("This case has not yet been implemented!")



class NonDimensionalisationSimpleExpressionVisitor(NonDimVis):
    r"""
    This Visitor converts unit-ful simple expressions with metric prefixes to real type expressions in the corresponding SI base unit in RHSs
    E.g.: Var_a V = ...... * 3MV -> Var_a V = ...... * (3 * 1.0E+06)
    """
    def __init__(self, preferred_prefix: Dict[str, str], model):
        super().__init__(preferred_prefix)
        self.model = model

    def visit_simple_expression(self, node):
        if node.get_numeric_literal() is not None:
            print("Numeric literal: " + str(node.get_numeric_literal()))
            if(isinstance(node.type, RealTypeSymbol)):
                print("\tReal number, no unit\n")
            elif (isinstance(node.type, UnitTypeSymbol)):
                # the expression 3 MV is a SimpleExpression for example
                parent_node = node.get_parent()
                print("\tUnit: " + str(node.type.unit.unit))
                conversion_factor = f"{super().get_conversion_factor_to_si(node.variable.name):.1E}"
                numeric_literal = node.get_numeric_literal()
                lhs_expression = ASTSimpleExpression(numeric_literal=float(numeric_literal), scope=node.get_scope())
                rhs_expression = ASTSimpleExpression(string=str(conversion_factor), scope=node.get_scope())
                if isinstance(parent_node, ASTExpression):
                    new_sub_node = ASTExpression(is_encapsulated=False,
                                                 binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                 lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                    new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope(),
                                             unary_operator=parent_node.unary_operator)
                    if parent_node.binary_operator is not None:
                        parent_node.binary_operator = parent_node.binary_operator
                        if parent_node.rhs == node:
                            parent_node.rhs = new_node
                        elif parent_node.lhs == node:
                            parent_node.lhs = new_node
                        else:
                            raise Exception("Node is neither lhs nor rhs of parent, possibly expression - should not execute until here.")
                    elif parent_node.binary_operator is None:
                        parent_node.rhs = None
                        parent_node.expression = new_node
                        parent_node.unary_operator = None
                    else:
                        raise Exception("This case is also possible and needs handling")
                if isinstance(parent_node, ASTDeclaration):
                    new_sub_node = ASTExpression(is_encapsulated=False,
                                                 binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                 lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                    new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())
                    parent_node.expression = new_node
                pass


            elif (isinstance(node.type, IntegerTypeSymbol)):
                print("\tInteger type number, no unit\n")
            else:
                raise Exception("Node type is neither RealTypeSymbol nor UnitTypeSymbol")
            return
        if node.function_call is None:
            if node.get_numeric_literal() is None:
                # get physical type of node
                if isinstance(node.type, UnitTypeSymbol):
                    if str(node.type.astropy_unit.physical_type) != 'unknown':
                        variable_physical_type_string = str(node.type.astropy_unit.physical_type)
                        # get preferred prefix for this node
                        preferred_prefix_this_node_string = f"{self.PREFIX_FACTORS[self.preferred_prefix[variable_physical_type_string]]:.1E}"
                        # create a new sub node that multiplies the variable with the reciprocal of the preferred prefix
                        lhs_expression = node.clone()
                        rhs_expression = ASTSimpleExpression(string=preferred_prefix_this_node_string, scope=node.get_scope())
                        new_sub_node = ASTExpression(is_encapsulated=False, binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                             lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                        # create new node encapsulating multiplication
                        parent_node = node.get_parent()
                        new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope(),
                                                         unary_operator=parent_node.unary_operator)
                        # attach new node to parent node
                        if node.get_parent().unary_operator is not None:
                            grandparent_node = parent_node.get_parent()
                            if parent_node == grandparent_node.lhs:
                                grandparent_node.lhs = new_node
                            if parent_node == parent_node.rhs:
                                grandparent_node.rhs = new_node
                        else:
                            if node == parent_node.lhs:
                                if parent_node.binary_operator is not None:
                                    parent_node.binary_operator = parent_node.binary_operator
                                    parent_node.lhs = new_node
                                    parent_node.rhs = parent_node.rhs
                                    pass
                                elif parent_node.binary_operator is None:
                                    parent_node.rhs = None
                                    parent_node.expression = new_node
                                    parent_node.unary_operator = None
                            if node == parent_node.rhs:
                                if parent_node.binary_operator is not None:
                                    parent_node.binary_operator = parent_node.binary_operator
                                    parent_node.rhs = new_node
                                    parent_node.lhs = parent_node.lhs
                                    pass
                                elif parent_node.binary_operator is None:
                                    parent_node.rhs = None
                                    parent_node.expression = new_node
                                    parent_node.unary_operator = None

        super().visit_simple_expression(node)


class NonDimensionalisationTransformer(Transformer):
    r"""Remove all units from the model and replace them with real type.

    NESTML model:
        V_m V = -70 mV

    generated code:
        float V_m = -0.07   # implicit: units of V
        float V_m = -70   # implicit: units of mV


    """

    # _default_options = {
    #     "quantity_to_preferred_prefix": {
    #         "time": "m",
    #         "voltage": "m"
    #     },
    #     "variable_to_preferred_prefix": {
    #         "V_m": "m",
    #         "V_dend": "u"
    #     }
    # }

    _default_options = {
        "quantity_to_preferred_prefix": {
        },
        "variable_to_preferred_prefix": {
        }
    }



    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform_(self, model: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        transformed_model = model.clone()

        variable_visitor = NonDimensionalisationVariableVisitor(self.get_option("quantity_to_preferred_prefix"))
        simple_expression_visitor = NonDimensionalisationSimpleExpressionVisitor(self.get_option("quantity_to_preferred_prefix"), model)
        declaration_visitor = NonDimensionalisationPreferredPrefixFactorOnRhsVisitor(self.get_option("quantity_to_preferred_prefix"), model)
        var_to_real_type_visitor = NonDimensionalisationVarToRealTypeVisitor(self.get_option("quantity_to_preferred_prefix"))

        transformed_model.accept(ASTParentVisitor())
        transformed_model.accept(variable_visitor)
        transformed_model.accept(simple_expression_visitor)
        transformed_model.accept(declaration_visitor)
        transformed_model.accept(var_to_real_type_visitor)
        transformed_model.accept(ASTSymbolTableVisitor())

        print("--------------------------------")
        print("model after transformation:")
        print("--------------------------------")
        print(transformed_model)
        with open("transformed_model_test_exp_in_equation_block.txt", "a") as f:
            f.write(str(transformed_model))

        return transformed_model

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
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
