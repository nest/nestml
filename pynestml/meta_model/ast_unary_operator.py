# -*- coding: utf-8 -*-
#
# ast_unary_operator.py
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


class ASTUnaryOperator(ASTNode):
    """
    This class is used to store a single unary operator, e.g., ~.
    Grammar:
        unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
    Attributes:
        is_unary_plus = False
        is_unary_minus = False
        is_unary_tilde = False
    """

    def __init__(self, is_unary_plus=False, is_unary_minus=False, is_unary_tilde=False, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_unary_plus: is a unary plus.
        :type is_unary_plus: bool
        :param is_unary_minus: is a unary minus.
        :type is_unary_minus: bool
        :param is_unary_tilde: is a unary tilde.
        :type is_unary_tilde: bool
        """
        assert ((is_unary_tilde + is_unary_minus + is_unary_plus) == 1), \
            '(PyNestML.AST.UnaryOperator) Type of unary operator not correctly specified!'
        super(ASTUnaryOperator, self).__init__(*args, **kwargs)
        self.is_unary_plus = is_unary_plus
        self.is_unary_minus = is_unary_minus
        self.is_unary_tilde = is_unary_tilde

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTUnaryOperator
        """
        dup = ASTUnaryOperator(is_unary_plus=self.is_unary_plus,
                               is_unary_minus=self.is_unary_minus,
                               is_unary_tilde=self.is_unary_tilde,
                               # ASTNode common attributes:
                               source_position=self.source_position,
                               scope=self.scope,
                               comment=self.comment,
                               pre_comments=[s for s in self.pre_comments],
                               in_comment=self.in_comment,
                               implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_parent(self, ast):
        """
        Indicates whether this node contains the handed over node.
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
        if not isinstance(other, ASTUnaryOperator):
            return False
        return (self.is_unary_minus == other.is_unary_minus
                and self.is_unary_plus == other.is_unary_plus
                and self.is_unary_tilde == other.is_unary_tilde)
