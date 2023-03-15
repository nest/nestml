# -*- coding: utf-8 -*-
#
# ast_comparison_operator.py
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


class ASTComparisonOperator(ASTNode):
    """
    This class is used to store a single comparison operator.
    Grammar:
        comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');
    Attributes:
        is_lt = False
        is_le = False
        is_eq = False
        is_ne = False
        is_ne2 = False
        is_ge = False
        is_gt = False
    """

    def __init__(self, is_lt=False, is_le=False, is_eq=False, is_ne=False, is_ne2=False, is_ge=False,
                 is_gt=False, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_lt: is less than operator.
        :type is_lt: bool
        :param is_le: is less equal operator.
        :type is_le: bool
        :param is_eq: is equality operator.
        :type is_eq: bool
        :param is_ne: is not equal operator.
        :type is_ne: bool
        :param is_ne2: is not equal operator (alternative syntax).
        :type is_ne2: bool
        :param is_ge: is greater equal operator.
        :type is_ge: bool
        :param is_gt: is greater than operator.
        :type is_gt: bool
        """
        assert ((is_lt + is_le + is_eq + is_ne + is_ne2 + is_ge + is_gt) == 1), \
            '(PyNestML.ASTComparisonOperator) Comparison operator not correctly specified!'
        super(ASTComparisonOperator, self).__init__(*args, **kwargs)
        self.is_gt = is_gt
        self.is_ge = is_ge
        self.is_ne2 = is_ne2
        self.is_ne = is_ne
        self.is_eq = is_eq
        self.is_le = is_le
        self.is_lt = is_lt

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTComparisonOperator
        """
        dup = ASTComparisonOperator(is_lt=self.is_lt,
                                    is_le=self.is_le,
                                    is_eq=self.is_eq,
                                    is_ne=self.is_ne,
                                    is_ne2=self.is_ne2,
                                    is_ge=self.is_ge,
                                    is_gt=self.is_gt,
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
        if not isinstance(other, ASTComparisonOperator):
            return False
        return (self.is_lt == other.is_lt and self.is_le == other.is_le
                and self.is_eq == other.is_eq and self.is_ne == other.is_ne
                and self.is_ne2 == other.is_ne2 and self.is_ge == other.is_ge and self.is_gt == other.is_gt)
