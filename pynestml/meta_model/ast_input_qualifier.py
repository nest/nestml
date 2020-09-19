# -*- coding: utf-8 -*-
#
# ast_input_qualifier.py
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


from pynestml.meta_model.ast_node import ASTNode


class ASTInputQualifier(ASTNode):
    """
    This class is used to store the qualifier of a buffer.
    ASTInputQualifier represents the qualifier of the input port. Only valid for spiking inputs.
    @attribute inhibitory true Indicates that this spiking input port is inhibitory.
    @attribute excitatory true Indicates that this spiking input port is excitatory.

    Grammar:
        inputQualifier : ('inhibitory' | 'excitatory');

    Attributes:
        is_inhibitory = False
        is_excitatory = False
    """

    def __init__(self, is_inhibitory=False, is_excitatory=False, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_inhibitory: is inhibitory buffer.
        :type is_inhibitory: bool
        :param is_excitatory: is excitatory buffer.
        :type is_excitatory: bool
        """
        super(ASTInputQualifier, self).__init__(*args, **kwargs)
        self.is_excitatory = is_excitatory
        self.is_inhibitory = is_inhibitory

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTInputQualifier
        """
        dup = ASTInputQualifier(is_excitatory=self.is_excitatory,
                                is_inhibitory=self.is_inhibitory,
                                # ASTNode common attributes:
                                source_position=self.source_position,
                                scope=self.scope,
                                comment=self.comment,
                                pre_comments=[s for s in self.pre_comments],
                                in_comment=self.in_comment,
                                post_comments=[s for s in self.post_comments],
                                implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: ASTNode
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: Optional[ASTNode]
        """
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInputQualifier):
            return False
        return self.is_excitatory == other.is_excitatory and self.is_inhibitory == other.is_inhibitory
