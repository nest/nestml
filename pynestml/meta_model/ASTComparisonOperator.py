#
# ASTComparisonOperator.py
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
from pynestml.meta_model.ASTNode import ASTNode


class ASTComparisonOperator(ASTNode):
    """
    This class is used to store a single comparison operator.
    Grammar:
        comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');
    """
    __isLt = False
    __isLe = False
    __isEq = False
    __isNe = False
    __isNe2 = False
    __isGe = False
    __isGt = False

    def __init__(self, is_lt=False, is_le=False, is_eq=False, is_ne=False, is_ne2=False, is_ge=False,
                 is_gt=False, source_position=None):
        """
        Standard constructor.
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
        :param source_position: the position of the element in the source
        :type source_position: ASTSourceLocation
        """
        assert ((is_lt + is_le + is_eq + is_ne + is_ne2 + is_ge + is_gt) == 1), \
            '(PyNestML.AST.ComparisonOperator) Comparison operator not correctly specified!'
        super(ASTComparisonOperator, self).__init__(source_position)
        self.__isGt = is_gt
        self.__isGe = is_ge
        self.__isNe2 = is_ne2
        self.__isNe = is_ne
        self.__isEq = is_eq
        self.__isLe = is_le
        self.__isLt = is_lt
        return

    def isLt(self):
        """
        Returns whether it is the less than operator.
        :return: True if less than operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isLt, bool) and self.__isLt

    def isLe(self):
        """
        Returns whether it is the less equal operator.
        :return: True if less equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isLe, bool) and self.__isLe

    def isEq(self):
        """
        Returns whether it is the equality operator.
        :return: True if less equality operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isEq, bool) and self.__isEq

    def isNe(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isNe, bool) and self.__isNe

    def isNe2(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isNe2, bool) and self.__isNe2

    def isGe(self):
        """
        Returns whether it is the greater equal operator.
        :return: True if less greater operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isGe, bool) and self.__isGe

    def isGt(self):
        """
        Returns whether it is the greater than operator.
        :return: True if less greater than, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isGt, bool) and self.__isGt

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTComparisonOperator):
            return False
        return (self.isLt() == other.isLt() and self.isLe() == other.isLe() and
                self.isEq() == other.isEq() and self.isNe() == other.isNe() and
                self.isNe2() == other.isNe2() and self.isGe() == other.isGe() and self.isGt() == other.isGt())
