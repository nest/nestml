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

from pynestml.meta_model.ASTDeclaration import ASTDeclaration
from pynestml.cocos.CoCo import CoCo
from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.utils.Logger import Logger
from pynestml.utils.Logger import LoggingLevel
from pynestml.utils.Messages import Messages
from pynestml.visitors.ASTVisitor import ASTVisitor


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
        assert isinstance(node, ASTDeclaration)
        if node.has_invariant():
            invariant_type = node.get_invariant().type
            if invariant_type is None or isinstance(invariant_type, ErrorTypeSymbol):
                code, message = Messages.get_type_could_not_be_derived(str(node.get_invariant()))
                Logger.log_message(error_position=node.get_invariant().get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.ERROR)
            elif not invariant_type.equals(PredefinedTypes.get_boolean_type()):
                code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_boolean_type(),
                                                                          invariant_type)
                Logger.log_message(error_position=node.get_invariant().get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.ERROR)
        return
