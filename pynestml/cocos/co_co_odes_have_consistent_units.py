# -*- coding: utf-8 -*-
#
# co_co_odes_have_consistent_units.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.symbol import SymbolKind
from astropy import units


class CoCoOdesHaveConsistentUnits(CoCo):
    """
    This coco ensures that whenever an ODE is defined, the physical unit of the left-hand side variable matches that of the right-hand side expression.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(OdeConsistentUnitsVisitor())


class OdeConsistentUnitsVisitor(ASTVisitor):

    def visit_ode_equation(self, node):
        """
        Checks the coco.
        :param node: A single ode equation.
        :type node: ast_ode_equation
        """
        variable_name = node.get_lhs().get_name()
        variable_symbol = node.get_lhs().get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if variable_symbol is None:
            code, message = Messages.get_variable_not_defined(variable_name)
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                               error_position=node.get_source_position())
            return
        variable_type = variable_symbol.type_symbol
        from pynestml.utils.unit_type import UnitType
        from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
        unit_type_name = "inv_diff_order_unit_type_" + variable_name + "'" * node.get_lhs().get_differential_order()
        inv_diff_order_unit_type = UnitType(name=unit_type_name, unit=1 / units.s**node.get_lhs().get_differential_order())
        inv_diff_order_unit_type_symbol = UnitTypeSymbol(inv_diff_order_unit_type)
        lhs_type = variable_type * inv_diff_order_unit_type_symbol
        rhs_type = node.get_rhs().type
        if not rhs_type.is_castable_to(lhs_type):
            code, message = Messages.get_ode_needs_consistent_units(
                variable_name, node.get_lhs().get_differential_order(), lhs_type, rhs_type)
            Logger.log_message(error_position=node.get_source_position(), code=code,
                               message=message, log_level=LoggingLevel.ERROR)
