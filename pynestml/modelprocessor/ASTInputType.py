#
# ASTInputType.py
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


from pynestml.modelprocessor.ASTNode import ASTNode


class ASTInputType(ASTNode):
    """
    This class is used to store the type of a buffer.
    ASTInputType represents the type of the input line e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
    Grammar:
        inputType : ('inhibitory' | 'excitatory');
    """
    is_inhibitory = False
    is_excitatory = False

    def __init__(self, is_inhibitory=False, is_excitatory=False, source_position=None):
        """
        Standard constructor.
        :param is_inhibitory: is inhibitory buffer.
        :type is_inhibitory: bool
        :param is_excitatory: is excitatory buffer.
        :type is_excitatory: book
        :param _sourcePosition: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTInputType, self).__init__(source_position)
        self.is_excitatory = is_excitatory
        self.is_inhibitory = is_inhibitory

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary ast node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def __str__(self):
        """
        Returns a string representation of the input type.
        :return: a string representation.
        :rtype: str
        """
        if self.is_inhibitory:
            return 'inhibitory'
        else:
            return 'excitatory'

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInputType):
            return False
        return self.is_excitatory == other.is_excitatory and self.is_inhibitory == other.is_inhibitory
