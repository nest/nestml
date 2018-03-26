#
# ASTLogicalOperator.py
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


class ASTLogicalOperator(ASTNode):
    """
    This class is used to store a single logical operator.
    Grammar:
        logicalOperator : (logicalAnd='and' | logicalOr='or');
    """
    __isLogicalAnd = False
    __isLogicalOr = False

    def __init__(self, _isLogicalAnd=False, _isLogicalOr=False, _sourcePosition=None):
        """
        Standard constructor.
        :param _isLogicalAnd: is logical and.
        :type _isLogicalAnd: bool
        :param _isLogicalOr: is logical or.
        :type _isLogicalOr: bool
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_isLogicalOr is None or isinstance(_isLogicalOr, bool)), \
            '(PyNestML.AST.LogicalOperator) Wrong type of is-logical-and provided (%s)!' % type(_isLogicalAnd)
        assert (_isLogicalAnd is None or isinstance(_isLogicalAnd, bool)), \
            '(PyNestML.AST.LogicalOperator) Wrong type of is-logical-or provided (%s)!' % type(_isLogicalOr)
        assert (_isLogicalAnd ^ _isLogicalOr), \
            '(PyNestML.AST.LogicalOperator) Logical operator not correctly specified!'
        super(ASTLogicalOperator, self).__init__(_sourcePosition)
        self.__isLogicalAnd = _isLogicalAnd
        self.__isLogicalOr = _isLogicalOr
        return

    def isAnd(self):
        """
        Returns whether it is an AND operator.
        :return: True if AND, otherwise False.
        :rtype: bool
        """
        return self.__isLogicalAnd

    def isOr(self):
        """
        Returns whether it is an OR operator.
        :return: True if OR, otherwise False.
        :rtype: bool
        """
        return self.__isLogicalOr

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def __str__(self):
        """
        Returns a string representing the operator.
        :return: a string representing the operator
        :rtype: str
        """
        if self.__isLogicalAnd:
            return ' and '
        else:
            return ' or '

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTLogicalOperator):
            return False
        return self.isAnd() == _other.isAnd() and self.isOr() == _other.isOr()
