#
# ASTUnaryOperator.py
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

from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTUnaryOperator(ASTElement):
    """
    This class is used to store a single unary operator, e.g., ~.
    Grammar:
        unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
    """
    __isUnaryPlus = False
    __isUnaryMinus = False
    __isUnaryTilde = False

    def __init__(self, _isUnaryPlus=False, _isUnaryMinus=False, _isUnaryTilde=False, _sourcePosition=None):
        """
        Standard constructor.
        :param _isUnaryPlus: is a unary plus.
        :type _isUnaryPlus: bool
        :param _isUnaryMinus: is a unary minus.
        :type _isUnaryMinus: bool
        :param _isUnaryTilde: is a unary tilde.
        :type _isUnaryTilde: bool
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_isUnaryTilde or _isUnaryMinus or _isUnaryPlus), '(PyNESTML.AST) Type of unary operator not specified.'
        super(ASTUnaryOperator, self).__init__(_sourcePosition)
        self.__isUnaryPlus = _isUnaryPlus
        self.__isUnaryMinus = _isUnaryMinus
        self.__isUnaryTilde = _isUnaryTilde

    @classmethod
    def makeASTUnaryOperator(cls, _isUnaryPlus=False, _isUnaryMinus=False, _isUnaryTilde=False, _sourcePosition=None):
        """
        The factory method of the ASTUnaryOperator class.
        :param _isUnaryPlus: is a unary plus.
        :type _isUnaryPlus: bool
        :param _isUnaryMinus: is a unary minus.
        :type _isUnaryMinus: bool
        :param _isUnaryTilde: is a unary tilde.
        :type _isUnaryTilde: bool
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTUnaryOperator object.
        :rtype: ASTUnaryOperator
        """
        return cls(_isUnaryPlus, _isUnaryMinus, _isUnaryTilde)

    def isUnaryPlus(self):
        """
        Returns whether it is a unary plus.
        :return: True if unary plus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryPlus

    def isUnaryMinus(self):
        """
        Returns whether it is a minus plus.
        :return: True if unary minus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryMinus

    def isUnaryTilde(self):
        """
        Returns whether it is a tilde plus.
        :return: True if unary tilde, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryTilde

    def printAST(self):
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isUnaryPlus:
            return '+'
        elif self.__isUnaryMinus:
            return '-'
        elif self.__isUnaryTilde:
            return '~'
        else:
            raise InvalidUnaryOperator('(PyNestML.AST.UnaryOperator.Print) Unary operator not specified!')


class InvalidUnaryOperator(Exception):
    """
    This exception is thrown whenever the unary operator has not been specified.
    """
    pass
