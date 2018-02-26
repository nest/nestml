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

from pynestml.modelprocessor.ASTElement import ASTElement
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ASTExpressionElement(ASTElement):
    """
    This class is not a part of the grammar but is used to store commonalities of all possible ast classes, e.g.,
    the source position. This class is abstract, thus no instances can be created.
    """
    __type = None
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

    @property
    def type(self):
        from pynestml.modelprocessor.ExpressionTypeVisitor import ExpressionTypeVisitor
        if self.__type is None:
            self.accept(ExpressionTypeVisitor())
        return self.__type

    @type.setter
    def type(self, _value):
        self.__type = _value
        return
