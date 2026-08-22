# -*- coding: utf-8 -*-
#
# co_co_no_assignment_to_unit.py
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
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNoAssignmentToUnit(CoCo):
    r"""
    This coco ensures that physical units are not assigned to.

    Not allowed:

    .. ::

        update:
            V += 1 mV


    However, note that the following is allowed:

    .. ::

        state:
            V mV = 123 mV

        update:
            V += 1 mV
    """

    @classmethod
    def check_co_co(cls, node: ASTModel):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        node.accept(CoCoNoAssignmentToUnitVisitor())


class CoCoNoAssignmentToUnitVisitor(ASTVisitor):
    def visit_assignment(self, node: ASTAssignment):
        """
        Ensures the coco.
        :param node: a single node.
        """
        symbol_as_type = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.TYPE)
        if not symbol_as_type:
            # the symbol cannot be resolved as a unit type, so the is definitely no assignment to a unit type here
            return

        # the variable can be resolved as a unit type. But is it actually a declared as a variable in the model?
        symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE)
        if not symbol:
            # it is not allowed to assign to a physical unit!
            code, message = Messages.get_not_allowed_to_assign_to_a_unit_type(str(node.get_variable()))
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
            return
