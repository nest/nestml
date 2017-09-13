"""
/*
 *  ASTBitOperator.py
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
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTBitOperator(ASTElement):
    """
    This class is used to store a single bit operator.
    Grammar:
        bitOperator : (bitAnd='&'| bitXor='^' | bitOr='|' | bitShiftLeft='<<' | bitShiftRight='>>');
    """
    __isBitAnd = False
    __isBitXor = False
    __isBitOr = False
    __isBitShiftLeft = False
    __isBitShiftRight = False

    def __init__(self, _isBitAnd=False, _isBitXor=False, _isBitOr=False, _isBitShiftLeft=False, _isBitShiftRight=False,
                 _sourcePosition=None):
        """
        Standard constructor.
        :param_sourcePosition: the position of the element in the source
        :type _sourcePosition: ASTSourcePosition
        :param _isBitAnd: is bit and operator.
        :type _isBitAnd: bool
        :param _isBitXor: is bit xor operator.
        :type _isBitXor: bool
        :param _isBitOr: is bit or operator.
        :type _isBitOr: bool
        :param _isBitShiftLeft: is bit shift left operator.
        :type _isBitShiftLeft: bool
        :param _isBitShiftRight: is bit shift right operator.
        :type _isBitShiftRight: bool
        """
        super(ASTBitOperator, self).__init__(_sourcePosition)
        self.__isBitShiftRight = _isBitShiftRight
        self.__isBitShiftLeft = _isBitShiftLeft
        self.__isBitOr = _isBitOr
        self.__isBitXor = _isBitXor
        self.__isBitAnd = _isBitAnd

    @classmethod
    def makeASTBitOperator(cls, _isBitAnd=False, _isBitXor=False, _isBitOr=False, _isBitShiftLeft=False,
                           _isBitShiftRight=False, _sourcePosition=None):
        """
        The factory method of the ASTBitOperator class.
        :param _isBitAnd: is bit and operator.
        :type _isBitAnd: bool
        :param _isBitXor: is bit xor operator.
        :type _isBitXor: bool
        :param _isBitOr: is bit or operator.
        :type _isBitOr: bool
        :param _isBitShiftLeft: is bit shift left operator.
        :type _isBitShiftLeft: bool
        :param _isBitShiftRight: is bit shift right operator.
        :type _isBitShiftRight: bool
        :param_sourcePosition: the position of the element in the source
        :type _sourcePosition: ASTSourcePosition
        :return: a new ASTBitOperator object.
        :rtype: ASTBitOperator
        """
        return cls(_isBitAnd, _isBitXor, _isBitOr, _isBitShiftLeft, _isBitShiftRight, _sourcePosition)

    def isBitAnd(self):
        """
        Returns whether it is the bit and operator.
        :return: True if bit and operator, otherwise False.
        :rtype: bool
        """
        return self.__isBitAnd

    def isBitOr(self):
        """
        Returns whether it is the bit or operator.
        :return: True if bit or operator, otherwise False.
        :rtype: bool
        """
        return self.__isBitOr

    def isBitXor(self):
        """
        Returns whether it is the bit xor operator.
        :return: True if bit xor operator, otherwise False.
        :rtype: bool
        """
        return self.__isBitXor

    def isBitShiftLeft(self):
        """
        Returns whether it is the bit shift left operator.
        :return: True if bit shift left operator, otherwise False.
        :rtype: bool
        """
        return self.__isBitShiftLeft

    def isBitShiftRight(self):
        """
        Returns whether it is the bit shift right operator.
        :return: True if bit shift right operator, otherwise False.
        :rtype: bool
        """
        return self.__isBitShiftRight

    def printAST(self):
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isBitAnd:
            return ' & '
        elif self.__isBitXor:
            return ' ^ '
        elif self.__isBitOr:
            return ' | '
        elif self.__isBitShiftLeft:
            return ' << '
        elif self.__isBitShiftRight:
            return ' >> '
        else:
            raise Exception("(NESTML) Bit operator not specified.")
