# -*- coding: utf-8 -*-
#
# co_co_equations_only_for_init_values.py
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
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoEquationsOnlyForInitValues(CoCo):
    """
    This coco ensures that ode equations are only provided for variables which have been defined in the
    initial_values block.
    Allowed:
        initial_values:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    Not allowed:
        state:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(EquationsOnlyForInitValues())


class EquationsOnlyForInitValues(ASTVisitor):
    """
    This visitor ensures that for all ode equations exists an initial value.
    """

    def visit_ode_equation(self, node):
        """
        Ensures the coco.
        :param node: a single equation object.
        :type node: ast_ode_equation
        """
        symbol = node.get_scope().resolve_to_symbol(node.get_lhs().get_name_of_lhs(), SymbolKind.VARIABLE)
        if symbol is not None and not symbol.is_init_values():
            code, message = Messages.get_equation_var_not_in_init_values_block(node.get_lhs().get_name_of_lhs())
            Logger.log_message(code=code, message=message,
                               error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            return
