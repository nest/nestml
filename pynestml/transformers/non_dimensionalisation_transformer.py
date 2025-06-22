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

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
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
class NonDimVis(ASTVisitor):
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__()
        self.preferred_prefix = preferred_prefix
        self.variable_original_metric_prefix_dict = dict()

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

class AddReciprocalOfPreferredPrefixVisitor(NonDimVis):
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)
        # self.preferred_prefix = preferred_prefix

    def visit_variable(self, node: ASTVariable) -> None:
        print("here!")



class NonDimensionalisationVisitor(NonDimVis):

    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__(preferred_prefix)


    def get_conversion_factor_to_si(self, from_unit_str):
        r"""
        Return the conversion factor from the unit we have in the NESTML file to SI units.
        """

        from_unit = u.Unit(from_unit_str)
        scale = from_unit.si.scale

        # to_scale = NonDimensionalisationVisitor.PREFIX_FACTORS[to_prefix_str]

        return scale

    # def visit_variable(self, node: ASTVariable) -> None:
    #     # TODO here the type needs to be changed to "real" and the name kept
    #     # TODO if the parent node of the variable is a declaration, the original metric prefix should be written to a dict{variable_name:original_metric_prefix}
    #     # TODO this prefix can then be propagated to the expressions where the variable_name is used
    #     # TODO ??? parameters block comes after equations block though, so dict can only be built after ???
    #     print("In visit_variable("+str(node)+")")
    #     if node.get_type_symbol():
    #         if(isinstance(node.get_type_symbol(), RealTypeSymbol)):
    #             print("\tReal number, no unit\n")
    #         elif (isinstance(node.get_type_symbol(), UnitTypeSymbol)):
    #             print("The unit is: "+str(node.get_type_symbol().unit.unit))
    #             print("The quantity is: "+str(node.get_type_symbol().unit.unit.physical_type))
    #
    #             parent_node = node.get_parent()
    #             # if isinstance(node, ASTVariable):
    #             #     # TODO
    #             #     original_metric_prefix = f"{self.get_conversion_factor_to_si(node.get_parent().expression.variable.name):.1E}"
    #             #     self.variable_original_metric_prefix_dict[parent_node.variables[0].name] = original_metric_prefix
    #
    #             new_node_type = RealTypeSymbol()
    #             new_variable = ASTVariable(name=node.name, type_symbol=new_node_type)
    #             new_data_type = ASTDataType(is_real=True, type_symbol=new_node_type)
    #
    #             if isinstance(parent_node, ASTDeclaration):
    #                 parent_node.variables[0] = new_variable
    #                 parent_node.data_type = new_data_type
    #                 pass
    #
    #
    #     # import pdb;pdb.set_trace()
    #
    #     # grab the prefix for this variable
    #     # XXX TODO
    #
    #     # find the corresponding desired prefix
    #     # XXX TODO
    #     if node.get_type_symbol() is None:
    #         if isinstance(node.get_parent(), ASTOdeEquation):
    #             pass
    #         elif (isinstance(node, ASTVariable) and node.get_parent().variable.name == node.get_name() and node.get_parent().numeric_literal == None):
    #             # Then the variable encountered is something like mV, without a numeric literal in front, e.g. (4 + 3) * mV
    #             conversion_factor = f"{self.get_conversion_factor_to_si(node.get_name()):.1E}"
    #             parent_node = node.get_parent()
    #             grandparent_node = parent_node.get_parent()
    #             rhs_expression = ASTSimpleExpression(string=str(conversion_factor), scope=node.get_scope())
    #             if grandparent_node.binary_operator is not None:
    #                 grandparent_node.rhs = rhs_expression
    #             pass
    #         # print("The preferred prefix for:"+str(u.get_physical_type(u.Unit(node.name)))+"is: "+self.preferred_prefix[str(u.get_physical_type(u.Unit(node.name)))])
    #         # desired_prefix = self.preferred_prefix[str(u.get_physical_type(u.Unit(node.name)))]
    #
    #         if isinstance(node.get_parent(), ASTSimpleExpression):
    #             if node.get_parent().is_numeric_literal():
    #                 # something like ``42 mA``. This is a ASTSimpleExpression. Remove the unit and replace with conversion factor
    #                 # conversion_factor = self.get_conversion_factor_to_si(node.name)
    #                 # parent_node = node.get_parent()
    #                 # parent_node.numeric_literal *= conversion_factor  # TODO this performs floating point arithmetic and leads to inaccuracies
    #                 # parent_node.variable = None
    #                 # parent_node.type = PredefinedTypes.get_real_type()
    #                 # # parent_node.get_children().remove(node)
    #
    #                 # conversion_factor = f"{self.get_conversion_factor_to_si(node.name):.1E}"
    #                 # parent_node = node.get_parent()
    #                 # numeric_literal = parent_node.get_numeric_literal()
    #                 # lhs_expression = ASTSimpleExpression(numeric_literal=float(numeric_literal))
    #                 # rhs_expression = ASTSimpleExpression(string=str(conversion_factor))
    #                 # new_sub_node = ASTExpression(is_encapsulated=False,
    #                 #                              binary_operator=ASTArithmeticOperator(is_times_op=True),
    #                 #                              lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
    #                 # new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())
    #                 #
    #                 #
    #                 # if isinstance(parent_node, ASTExpression):
    #                 #     parent_node.rhs = new_node
    #                 #     pass
    #                 pass
    #             else:
    #                 # something like ``I_foo``
    #                 parent_node = node.get_parent()
    #                 if isinstance(parent_node, ASTSimpleExpression) and isinstance(parent_node.type, RealTypeSymbol):
    #                     print("real type variable: " + node.name)
    #                 # conversion_factor = 42
    #                 # # conversion_factor = self.PREFIX_FACTORS[self.preferred_prefix[str(u.get_physical_type(u.Unit(node.name)))]] # XXX TODO
    #                 #
    #                 # new_sub_node_lhs = ASTSimpleExpression(numeric_literal=conversion_factor)
    #                 # new_sub_node_rhs = ASTSimpleExpression(variable=node)
    #                 # new_sub_node = ASTExpression(binary_operator=ASTArithmeticOperator(is_times_op=True), lhs=new_sub_node_lhs, rhs=new_sub_node_rhs)
    #                 # new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node)
    #                 #
    #                 #
    #                 # assert parent_node.is_variable()
    #                 #
    #                 # grandparent_node = parent_node.get_parent()
    #                 # if isinstance(grandparent_node, ASTExpression):
    #                 #     if grandparent_node.lhs == parent_node:
    #                 #         grandparent_node.lhs = new_node
    #                 #     else:
    #                 #         assert grandparent_node.rhs == parent_node
    #                 #         grandparent_node.rhs = new_node
    #                 else:
    #                     # raise Exception("This case has not yet been implemented!")
    #                     pass
    #
    #
    #         else:
    #             pass
    #             # raise Exception("This case has not yet been implemented!")

        # multiply by the right conversion factor into the expression
        # XXX TODO

        # change variable type
        # XXX TODO

        # for quantity, preferred_prefix in self.preferred_prefix.items():
        #     pass

    def visit_simple_expression(self, node):
        if node.get_numeric_literal() is not None:
            print("Numeric literal: " + str(node.get_numeric_literal()))
            if(isinstance(node.type, RealTypeSymbol)):
                print("\tReal number, no unit\n")
            elif (isinstance(node.type, UnitTypeSymbol)):
                # the expression 3 MV is a SimpleExpression for example
                parent_node = node.get_parent()
                print("\tUnit: " + str(node.type.unit.unit))
                conversion_factor = f"{self.get_conversion_factor_to_si(node.variable.name):.1E}"
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
                        parent_node.rhs = new_node
                        # self.visit(parent_node)
                        # return
                        pass
                    elif parent_node.binary_operator is None:
                        parent_node.rhs = None
                        parent_node.expression = new_node
                        parent_node.unary_operator = None
                        # super().visit_expression(parent_node.expression)
                        # return
                    else:
                        raise Exception("This case is also possible and needs handling")
                    pass
                if isinstance(parent_node, ASTDeclaration):
                    new_sub_node = ASTExpression(is_encapsulated=False,
                                                 binary_operator=ASTArithmeticOperator(is_times_op=True),
                                                 lhs=lhs_expression, rhs=rhs_expression, scope=node.get_scope())
                    new_node = ASTExpression(is_encapsulated=True, expression=new_sub_node, scope=node.get_scope())
                    parent_node.expression = new_node
                pass
            # TODO once this is done the rest of the children should not be visited, as for example 70mV -> mV is
            #  a child node and would also be transformed by visit_variable() in this transformer
            #  How do I do this?


            elif (isinstance(node.type, IntegerTypeSymbol)):
                print("\tInteger type number, no unit\n")
            else:
                raise Exception("Node type is neither RealTypeSymbol nor UnitTypeSymbol")
            return

        super().visit_simple_expression(node)
        # super().visit_simple_expression(node.get_parent())

    def visit_assignment(self, node: ASTAssignment):
        # XXX TODO: insert conversion factor for LHS
        pass

    def visit_ode_equation(self, node: ASTOdeEquation):
        # XXX TODO: insert conversion factor for LHS
        pass

    def visit_inline_expression(self, node: ASTInlineExpression):
        # XXX TODO: insert conversion factor for LHS
        pass

    def visit_declaration(self, node: ASTDeclaration):
        # XXX TODO: insert conversion factor for LHS
        pass

    # @classmethod
    # def get_factor(cls, unit: units.UnitBase) -> float:
    #     """
    #     Gives a factor for a given unit that transforms it to a "neuroscience" scale. If the given unit is not listed as a neuroscience unit, the factor is 1.

    #     :param unit: an astropy unit
    #     :type unit: IrreducibleUnit or Unit or CompositeUnit
    #     :return: a factor to that unit, converting it to "neuroscience" scales.
    #     """

    #     # check if it is dimensionless, thus only a prefix
    #     if unit.physical_type == 'dimensionless':
    #         return unit.si

    #     # otherwise check if it is one of the base units
    #     target_unit = None
    #     if unit.physical_type == 'electrical conductance':
    #         target_unit = units.nS

    #     if unit.physical_type == 'electrical resistance':
    #         target_unit = units.Gohm

    #     if unit.physical_type == 'time':
    #         target_unit = units.ms

    #     if unit.physical_type == 'electrical capacitance':
    #         target_unit = units.pF

    #     if unit.physical_type == 'electrical potential':
    #         target_unit = units.mV

    #     if unit.physical_type == 'electrical current':
    #         target_unit = units.pA

    #     if target_unit is not None:
    #         return (unit / target_unit).si.scale

    #     if unit == unit.bases[0] and len(unit.bases) == 1:
    #         # this case means that we stuck in a recursive definition
    #         # just return the factor 1.0
    #         return 1.0

    #     # now if it is not a base unit, it has to be a combined one, e.g. s**2, decompose it
    #     factor = 1.0
    #     for i in range(0, len(unit.bases)):
    #         factor *= cls.get_factor(unit.bases[i]) ** unit.powers[i]
    #     return factor




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

        # transformed_model.accept(ASTSymbolTableVisitor())
        transformed_model.accept(ASTParentVisitor())


        visitor = NonDimensionalisationVisitor(self.get_option("quantity_to_preferred_prefix"))
        transformed_model.accept(visitor)
        transformed_model.accept(ASTSymbolTableVisitor())

        print("--------------------------------")
        print("model after transformation:")
        print("--------------------------------")
        print(transformed_model)
        with open("transformed_model.txt", "a") as f:
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
