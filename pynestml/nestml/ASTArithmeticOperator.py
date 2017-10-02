#
# ASTArithmeticOperator.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


from pynestml.nestml.ASTElement import ASTElement


class ASTArithmeticOperator(ASTElement):
    """
    This class is used to store a single arithmetic operator, e.g. +.
    No grammar. This part is defined outside the grammar to make processing and storing of models easier and 
    comprehensible.
    """
    __isTimesOp = False
    __isDivOp = False
    __isModuloOp = False
    __isPlusOp = False
    __isMinusOp = False
    __isPowOp = False

    def __init__(self, _isTimesOp=False, _isDivOp=False, _isModuloOp=False, _isPlusOp=False, _isMinusOp=False,
                 _isPowOp=False, _sourcePosition=None):
        """
        Standard constructor.
        :param _isTimesOp: is the times operator.
        :type _isTimesOp: bool
        :param _isDivOp: is div operator.
        :type _isDivOp: bool
        :param _isModuloOp: is the modulo operator.
        :type _isModuloOp: bool
        :param _isPlusOp: is the plus operator.
        :type _isPlusOp: bool
        :param _isMinusOp: is the minus operator.
        :type _isMinusOp: bool
        :param _isPowOp: is a power operator.
        :type _isPowOp: bool
        :param _sourcePosition: the position of this element in the source file
        :type _sourcePosition: ASTSourcePosition
        """
        assert (_isTimesOp is not None and isinstance(_isTimesOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-times parameter provided (%s)!' % type(_isTimesOp)
        assert (_isDivOp is not None and isinstance(_isDivOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-div parameter provided (%s)!' % type(_isDivOp)
        assert (_isModuloOp is not None and isinstance(_isModuloOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-mod parameter provided (%s)!' % type(_isModuloOp)
        assert (_isPlusOp is not None and isinstance(_isPlusOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-plus parameter provided (%s)!' % type(_isPlusOp)
        assert (_isMinusOp is not None and isinstance(_isMinusOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-minus parameter provided (%s)!' % type(_isMinusOp)
        assert (_isPowOp is not None and isinstance(_isPowOp, bool)), \
            '(PyNESTML.AST.ArithmeticOperator) wrong type of is-pow parameter provided (%s)!' % type(_isPowOp)
        assert (_isTimesOp or _isDivOp or _isModuloOp or _isPlusOp or _isMinusOp or _isPowOp), \
            '(PyNESTML.AST.ArithmeticOperator) Type of arithmetic operator not specified.'
        super(ASTArithmeticOperator, self).__init__(_sourcePosition)
        self.__isTimesOp = _isTimesOp
        self.__isDivOp = _isDivOp
        self.__isModuloOp = _isModuloOp
        self.__isPlusOp = _isPlusOp
        self.__isMinusOp = _isMinusOp
        self.__isPowOp = _isPowOp
        return

    @classmethod
    def makeASTArithmeticOperator(cls, _isTimesOp=False, _isDivOp=False, _isModuloOp=False,
                                  _isPlusOp=False, _isMinusOp=False, _isPowOp=False, _sourcePosition=None):
        """
        The factory method of the ASTArithmeticOperator class.
        :param _sourcePosition: the source position of the element
        :type _sourcePosition: ASTSourcePosition 
        :param _isTimesOp: is the times operator.
        :type _isTimesOp: bool
        :param _isDivOp: is div operator.
        :type _isDivOp: bool
        :param _isModuloOp: is the modulo operator.
        :type _isModuloOp: bool
        :param _isPlusOp: is the plus operator.
        :type _isPlusOp: bool
        :param _isMinusOp: is the minus operator.
        :type _isMinusOp: bool
        :param _isPowOp: is a power operator.
        :type _isPowOp: bool
        :param _sourcePosition: the position of this element in the source file
        :type _sourcePosition: ASTSourcePosition
        :return: a new ASTArithmeticOperator object.
        :rtype: ASTArithmeticOperator
        """
        return cls(_isTimesOp, _isDivOp, _isModuloOp, _isPlusOp, _isMinusOp, _isPowOp, _sourcePosition)

    def isTimesOp(self):
        """
        Returns whether it is a times operator or not.
        :return: True if times operator, otherwise False.
        :rtype: bool
        """
        return self.__isTimesOp

    def isDivOp(self):
        """
        Returns whether it is a div operator or not.
        :return: True if div operator, otherwise False.
        :rtype: bool
        """
        return self.__isDivOp

    def isModuloOp(self):
        """
        Returns whether it is a modulo operator or not.
        :return: True if modulo operator, otherwise False.
        :rtype: bool
        """
        return self.__isModuloOp

    def isPlusOp(self):
        """
        Returns whether it is a plus operator or not.
        :return: True if plus operator, otherwise False.
        :rtype: bool
        """
        return self.__isPlusOp

    def isMinusOp(self):
        """
        Returns whether it is a minus operator or not.
        :return: True if minus operator, otherwise False.
        :rtype: bool
        """
        return self.__isMinusOp

    def isPowOp(self):
        """
        Returns whether it is a power operator or not.
        :return: True if power operator, otherwise False.
        :rtype: bool
        """
        return self.__isPowOp

    def printAST(self):
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isTimesOp:
            return ' * '
        elif self.__isDivOp:
            return ' / '
        elif self.__isModuloOp:
            return ' % '
        elif self.__isPlusOp:
            return ' + '
        elif self.__isMinusOp:
            return ' - '
        elif self.__isPowOp:
            return ' ** '
        else:
            raise InvalidArithmeticOperator('(PyNestML.ArithmeticOperator.Print) Arithmetic operator not specified.')

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None


class InvalidArithmeticOperator(Exception):
    """
    This exception is thrown whenever the arithmetic operator has not been specified.
    """
    pass
