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
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
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



class NonDimensionalisationVisitor(ASTVisitor):
    def __init__(self, preferred_prefix: Dict[str, str]):
        super().__init__()
        self.preferred_prefix = preferred_prefix

    def get_conversion_factor_to_desired(self, from_unit_str, to_unit_str, to_unit_base_unit):
        try:
            from_unit = u.Unit(from_unit_str)

            # If to_unit_str is "1", interpret it as the base unit of the same physical type
            if to_unit_str == "1":
                physical_type = from_unit.physical_type
                # Get canonical base unit for that physical type
                to_unit = physical_type._physical_type_id[0][0]
            else:
                # Target unit is desired prefix concatenated with base unit for corresponding physical type
                to_unit = u.Unit(to_unit_str+str(to_unit_base_unit))

            # Compute the scale factor (no value, just unit scaling)
            return from_unit.to(to_unit)

        except:
            raise ValueError(f"Invalid unit")

    def visit_variable(self, node: ASTVariable) -> None:
        print("In visit_variable("+str(node)+")")
        if node.get_type_symbol():
            print("The unit is: "+str(node.get_type_symbol().unit.unit))
            print("The quantity is: "+str(node.get_type_symbol().unit.unit.physical_type))

        # import pdb;pdb.set_trace()

        # grab the prefix for this variable
        # XXX TODO


        # find the corresponding desired prefix
        # XXX TODO
        if node.get_type_symbol() is None: # add check if node name can be interpreted as astropy unit
            print("The preferred prefix for:"+str(u.get_physical_type(u.Unit(node.name)))+"is: "+self.preferred_prefix[str(u.get_physical_type(u.Unit(node.name)))])
            desired_prefix = self.preferred_prefix[str(u.get_physical_type(u.Unit(node.name)))]
            to_unit_base_unit = u.get_physical_type(u.Unit(node.name))._unit
            conversion_factor = self.get_conversion_factor_to_desired(node.name, desired_prefix, to_unit_base_unit)
            new_expression_string = "*"+str(conversion_factor)
        # multiply by the right conversion factor into the expression
        # XXX TODO

        # change variable type
        # XXX TODO

        for quantity, preferred_prefix in self.preferred_prefix.items():
            pass

    def visit_simple_expression(self, node):
        if node.get_numeric_literal() is not None:
            print("Numeric literal: " + str(node.get_numeric_literal()))
            print("\tUnit: " + str(node.type.unit.unit))
            return

        super().visit_simple_expression(node)

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

        visitor = NonDimensionalisationVisitor(self.get_option("quantity_to_preferred_prefix"))
        transformed_model.accept(visitor)

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
