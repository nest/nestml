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

from pynestml.modelprocessor.ASTNode import ASTNode


class ASTUnaryOperator(ASTNode):
    """
    This class is used to store a single unary operator, e.g., ~.
    Grammar:
        unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
    """
    __isUnaryPlus = False
    __isUnaryMinus = False
    __isUnaryTilde = False

    def __init__(self, _isUnaryPlus=False, _isUnaryMinus=False, _isUnaryTilde=False, source_position=None):
        """
        Standard constructor.
        :param _isUnaryPlus: is a unary plus.
        :type _isUnaryPlus: bool
        :param _isUnaryMinus: is a unary minus.
        :type _isUnaryMinus: bool
        :param _isUnaryTilde: is a unary tilde.
        :type _isUnaryTilde: bool
        :param source_position: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_isUnaryMinus is None or isinstance(_isUnaryMinus, bool)), \
            '(PyNestML.AST.UnaryOperator) Wrong type of unary minus provided (%s)!' % type(_isUnaryMinus)
        assert (_isUnaryMinus is None or isinstance(_isUnaryMinus, bool)), \
            '(PyNestML.AST.UnaryOperator) Wrong type of unary plus provided (%s)!' % type(_isUnaryPlus)
        assert (_isUnaryMinus is None or isinstance(_isUnaryMinus, bool)), \
            '(PyNestML.AST.UnaryOperator) Wrong type of unary tilde provided (%s)!' % type(_isUnaryTilde)
        assert ((_isUnaryTilde + _isUnaryMinus + _isUnaryPlus) == 1), \
            '(PyNestML.AST.UnaryOperator) Type of unary operator not correctly specified!'
        super(ASTUnaryOperator, self).__init__(source_position)
        self.__isUnaryPlus = _isUnaryPlus
        self.__isUnaryMinus = _isUnaryMinus
        self.__isUnaryTilde = _isUnaryTilde
        return

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
        if self.__isUnaryPlus:
            return '+'
        elif self.__isUnaryMinus:
            return '-'
        elif self.__isUnaryTilde:
            return '~'
        else:
            raise RuntimeError('Type of unary operator not specified!')

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTUnaryOperator):
            return False
        return self.isUnaryMinus() == _other.isUnaryMinus() and self.isUnaryPlus() == _other.isUnaryPlus() and \
               self.isUnaryTilde() == _other.isUnaryTilde()
