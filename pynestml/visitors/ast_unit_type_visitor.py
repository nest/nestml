# -*- coding: utf-8 -*-
#
# ast_unit_type_visitor.py
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
from astropy import units

from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.unit_type import UnitType
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTUnitTypeVisitor(ASTVisitor):
    """
    A visitor for the ASTUnitType class that visits all the unit types and resolves them into their unit type symbols.
    """

    def __init__(self):
        super().__init__()
        self.symbol = None

    def visit_unit_type(self, node):
        """
        Visits a single unit type element, checks for correct usage of units and builds the corresponding combined
        unit.
        :param node: a single unit type meta_model.
        :type node: ASTUnitType
        :return: a new type symbol representing this unit type.
        """

        if node.is_simple_unit():
            type_s = PredefinedTypes.get_type(node.unit)
            if type_s is None:
                code, message = Messages.unknown_type(str(node.unit))
                Logger.log_message(None, code, message, node.get_source_position(), LoggingLevel.ERROR)
                return

            node.set_type_symbol(type_s)
            self.symbol = type_s

    def endvisit_unit_type(self, node):
        if node.is_encapsulated:
            node.set_type_symbol(node.compound_unit.get_type_symbol())
        elif node.is_pow:
            base_symbol = node.base.get_type_symbol()
            exponent = node.exponent
            astropy_unit = base_symbol.astropy_unit ** exponent
            res = handle_unit(astropy_unit)
            node.set_type_symbol(res)
            self.symbol = res
        elif node.is_div:
            if isinstance(node.get_lhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                lhs = node.get_lhs().get_type_symbol().astropy_unit
            else:
                lhs = node.get_lhs()
            rhs = node.get_rhs().get_type_symbol().astropy_unit
            res = lhs / rhs
            res = handle_unit(res)
            node.set_type_symbol(res)
            self.symbol = res
        elif node.is_times:
            if isinstance(node.get_lhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                if node.get_lhs().get_type_symbol() is None or isinstance(node.get_lhs().get_type_symbol(),
                                                                          ErrorTypeSymbol):
                    node.set_type_symbol(ErrorTypeSymbol())
                    return
                lhs = node.get_lhs().get_type_symbol().astropy_unit
            else:
                lhs = node.get_lhs()
            rhs = node.get_rhs().get_type_symbol().astropy_unit
            res = lhs * rhs
            res = handle_unit(res)
            node.set_type_symbol(res)
            self.symbol = res
        return


def handle_unit(unit_type):
    """
    Handles a handed over unit by creating the corresponding unit-type, storing it in the list of predefined
    units, creating a type symbol and returning it.
    :param unit_type: astropy unit object
    :type unit_type: astropy.units.core.Unit
    :return: a new type symbol
    """
    # first ensure that it does not already exists, if not create it and register it in the set of predefined units
    # first clean up the unit of not required components, here it is the 1.0 in front of the unit
    # e.g., 1.0 * 1 / ms. This step is not mandatory for correctness, but makes  reporting easier
    if isinstance(unit_type, units.Quantity) and unit_type.value == 1.0:
        to_process = unit_type.unit
    else:
        to_process = unit_type
    if str(to_process) not in PredefinedUnits.get_units().keys():
        unit_type_t = UnitType(name=str(to_process), unit=to_process)
        PredefinedUnits.register_unit(unit_type_t)
    # now create the corresponding type symbol if it does not exists
    if PredefinedTypes.get_type(str(to_process)) is None:
        type_symbol = UnitTypeSymbol(unit=PredefinedUnits.get_unit(str(to_process)))
        PredefinedTypes.register_type(type_symbol)
    return PredefinedTypes.get_type(name=str(to_process))
