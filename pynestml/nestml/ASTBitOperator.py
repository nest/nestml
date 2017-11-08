#
# ASTBitOperator.py
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

from pynestml.nestml.ASTElement import ASTElement


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
        assert (_isBitAnd is not None and isinstance(_isBitAnd, bool)), \
            '(PyNestML.AST.BitOperator) No or wrong typ of is-bit-and provided (%s)!' % type(_isBitAnd)
        assert (_isBitOr is not None and isinstance(_isBitOr, bool)), \
            '(PyNestML.AST.BitOperator) No or wrong typ of is-bit-or provided (%s)!' % type(_isBitOr)
        assert (_isBitXor is not None and isinstance(_isBitXor, bool)), \
            '(PyNestML.AST.BitOperator) No or wrong typ of is-bit-xor provided (%s)!' % type(_isBitXor)
        assert (_isBitShiftLeft is not None and isinstance(_isBitShiftLeft, bool)), \
            '(PyNestML.AST.BitOperator) No or wrong typ of is-bit-shift-left provided (%s)!' % type(_isBitShiftLeft)
        assert (_isBitShiftRight is not None and isinstance(_isBitShiftRight, bool)), \
            '(PyNestML.AST.BitOperator) No or wrong typ of is-bit-shift-right provided (%s)!' % type(_isBitShiftRight)
        assert ((_isBitAnd + _isBitOr + _isBitXor + _isBitShiftLeft + _isBitShiftRight) == 1),\
            '(PyNestML.AST.BitOperator) Bit operator not correctly specified!'
        super(ASTBitOperator, self).__init__(_sourcePosition)
        self.__isBitShiftRight = _isBitShiftRight
        self.__isBitShiftLeft = _isBitShiftLeft
        self.__isBitOr = _isBitOr
        self.__isBitXor = _isBitXor
        self.__isBitAnd = _isBitAnd
        return

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
        return isinstance(self.__isBitAnd, bool) and self.__isBitAnd

    def isBitOr(self):
        """
        Returns whether it is the bit or operator.
        :return: True if bit or operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isBitOr, bool) and self.__isBitOr

    def isBitXor(self):
        """
        Returns whether it is the bit xor operator.
        :return: True if bit xor operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isBitXor, bool) and self.__isBitXor

    def isBitShiftLeft(self):
        """
        Returns whether it is the bit shift left operator.
        :return: True if bit shift left operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isBitShiftLeft, bool) and self.__isBitShiftLeft

    def isBitShiftRight(self):
        """
        Returns whether it is the bit shift right operator.
        :return: True if bit shift right operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isBitShiftRight, bool) and self.__isBitShiftRight

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
            raise RuntimeError('Type of bit operator not specified!')

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTBitOperator):
            return False
        return self.isBitAnd() == _other.isBitAnd() and self.isBitOr() == _other.isBitOr() and \
               self.isBitXor() == _other.isBitXor() and self.isBitShiftLeft() == self.isBitShiftLeft() and \
               self.isBitShiftRight() == _other.isBitShiftRight()
