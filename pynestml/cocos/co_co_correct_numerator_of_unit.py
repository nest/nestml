# -*- coding: utf-8 -*-
#
# co_co_correct_numerator_of_unit.py
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


class CoCoCorrectNumeratorOfUnit(CoCo):
    """
    This coco ensures that all units which consist of a dividend and divisor, where the numerator is a numeric
    value, have 1 as the numerator.
    Allowed:
        V_m 1/mV = ...
    Not allowed:
        V_m 2/mV = ...
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(NumericNumeratorVisitor())


class NumericNumeratorVisitor(ASTVisitor):
    """
    Visits a numeric numerator and checks if the value is 1.
    """

    def visit_unit_type(self, node):
        """
        Check if the coco applies,
        :param node: a single unit type object.
        :type node: ast_unit_type
        """
        if node.is_div and isinstance(node.lhs, int) and node.lhs != 1:
            from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
            node.set_type_symbol(ErrorTypeSymbol())
            code, message = Messages.get_wrong_numerator(str(node))
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
