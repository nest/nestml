# -*- coding: utf-8 -*-
#
# ast_bit_operator.py
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


class ASTBitOperator(ASTNode):
    """
    This class is used to store a single bit operator.
    Grammar:
        bitOperator : (bitAnd='&'| bitXor='^' | bitOr='|' | bitShiftLeft='<<' | bitShiftRight='>>');
    Attributes:
        is_bit_and = False
        is_bit_xor = False
        is_bit_or = False
        is_bit_shift_left = False
        is_bit_shift_right = False
    """

    def __init__(self, is_bit_and=False, is_bit_xor=False, is_bit_or=False, is_bit_shift_left=False,
                 is_bit_shift_right=False, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_bit_and: is bit and operator.
        :type is_bit_and: bool
        :param is_bit_xor: is bit xor operator.
        :type is_bit_xor: bool
        :param is_bit_or: is bit or operator.
        :type is_bit_or: bool
        :param is_bit_shift_left: is bit shift left operator.
        :type is_bit_shift_left: bool
        :param is_bit_shift_right: is bit shift right operator.
        :type is_bit_shift_right: bool
        """
        super(ASTBitOperator, self).__init__(*args, **kwargs)
        self.is_bit_shift_right = is_bit_shift_right
        self.is_bit_shift_left = is_bit_shift_left
        self.is_bit_or = is_bit_or
        self.is_bit_xor = is_bit_xor
        self.is_bit_and = is_bit_and

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTBitOperator
        """
        dup = ASTBitOperator(is_bit_shift_right=self.is_bit_shift_right,
                             is_bit_shift_left=self.is_bit_shift_left,
                             is_bit_or=self.is_bit_or,
                             is_bit_xor=self.is_bit_xor,
                             is_bit_and=self.is_bit_and,
                             # ASTNode common attriutes:
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
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
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
        if not isinstance(other, ASTBitOperator):
            return False
        return (self.is_bit_and == other.is_bit_and and self.is_bit_or == other.is_bit_or
                and self.is_bit_xor == other.is_bit_xor and self.is_bit_shift_left == self.is_bit_shift_left
                and self.is_bit_shift_right == other.is_bit_shift_right)
