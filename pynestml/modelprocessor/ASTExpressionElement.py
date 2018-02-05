#
# ASTElifClause.py
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
from abc import ABCMeta, abstractmethod

from pynestml.modelprocessor.ASTNode import ASTElement
from pynestml.modelprocessor.Either import Either


class ASTExpressionElement(ASTElement):
    """
    This class is not a part of the grammar but is used to store commonalities of all possible ast classes, e.g.,
    the source position. This class is abstract, thus no instances can be created.
    """
    __typeEither = None
    __metaclass__ = ABCMeta

    def __init__(self, _sourcePosition=None, _scope=None):
        super().__init__(_sourcePosition, _scope)

    @abstractmethod
    def equals(self, _other=None):
        pass

    @abstractmethod
    def getParent(self, _ast=None):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def setTypeEither(self, _typeEither=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeEither: a single type symbol object.
        :type _typeEither: TypeSymbol
        """
        assert (_typeEither is not None and isinstance(_typeEither, Either)), \
            '(PyNestML.AST.Expression) No or wrong type of type symbol provided (%s)!' % type(_typeEither)
        self.__typeEither = _typeEither
        return

    def getTypeEither(self):
        """
        Returns an Either object holding either the type symbol of
        this expression or the corresponding error message
        If it does not exist, run the ExpressionTypeVisitor on it to calculate it
        :return: Either a valid type or an error message
        :rtype: Either
        """
        if self.__typeEither is None:
            from pynestml.modelprocessor.ExpressionTypeVisitor import ExpressionTypeVisitor
            self.accept(ExpressionTypeVisitor())
        return self.__typeEither
