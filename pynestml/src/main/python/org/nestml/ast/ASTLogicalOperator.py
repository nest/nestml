"""
/*
 *  ASTLogicalOperator.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
 @author kperun
"""


class ASTLogicalOperator:
    """
    This class is used to store a single logical operator.
    Grammar:
        logicalOperator : (logicalAnd='and' | logicalOr='or');
    """
    __isLogicalAnd = False
    __isLogicalOr = False

    def __init__(self, _isLogicalAnd=False, _isLogicalOr=False):
        """
        Standard constructor.
        :param _isLogicalAnd: is logical and.
        :type _isLogicalAnd: bool
        :param _isLogicalOr: is logical or.
        :type _isLogicalOr: bool
        """
        assert _isLogicalAnd ^ _isLogicalOr, "(NESTML) Only one operator allowed."
        self.__isLogicalAnd = _isLogicalAnd
        self.__isLogicalOr = _isLogicalOr

    @classmethod
    def makeASTLogicalOperator(cls, _isLogicalAnd=False, _isLogicalOr=False):
        """
        The factory method of the ASTLogicalOperator class.
        :param _isLogicalAnd: is logical and.
        :type _isLogicalAnd: bool
        :param _isLogicalOr: is logical or.
        :type _isLogicalOr: bool
        :return: a new ASTLogicalOperator object.
        :rtype: ASTLogicalOperator
        """
        return cls(_isLogicalAnd, _isLogicalOr)

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

    def printAST(self):
        """
        Returns a string representing the operator.
        :return: a string representing the operator
        :rtype: str
        """
        if self.__isLogicalAnd:
            return ' and '
        else:
            return ' or '
