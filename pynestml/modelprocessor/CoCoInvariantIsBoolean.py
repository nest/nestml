#
# CoCoInvariantIsBoolean.py
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

from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


class CoCoInvariantIsBoolean(CoCo):
    """
    This coco checks that all invariants are of type boolean

    """

    @classmethod
    def check_co_co(cls, neuron):
        """
        Ensures the coco for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        visitor = InvariantTypeVisitor()
        neuron.accept(visitor)
        

class InvariantTypeVisitor(ASTVisitor):
    """
    Checks if for each invariant, the type is boolean.
    """

    def visit_declaration(self, node):
        """
        Checks the coco for a declaration.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        if node.has_invariant():
            invariant_type = node.get_invariant().get_type_either()
            if invariant_type is None or invariant_type.isError():
                code, message = Messages.getTypeCouldNotBeDerived(str(node.get_invariant()))
                Logger.log_message(error_position=node.get_invariant().get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.ERROR)
            elif not invariant_type.getValue().equals(PredefinedTypes.getBooleanType()):
                code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                      invariant_type.getValue())
                Logger.log_message(error_position=node.get_invariant().get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.ERROR)
        return
