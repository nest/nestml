#
# ASTElement.py
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


from abc import ABCMeta
from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope


class ASTElement:
    """
    This class is not a part of the grammar but is used to store commonalities of all possible ast classes, e.g.,
    the source position. This class is abstract, thus no instances can be created.
    """
    __metaclass__ = ABCMeta
    __sourcePosition = None
    __scope = None

    def __init__(self, _sourcePosition=None, _scope=None):
        """
        The standard constructor.
        :param _sourcePosition: a source position element.
        :type _sourcePosition: ASTSourcePosition
        :param _scope: the scope in which this element is embedded in.
        :type _scope: Scope
        """
        assert (_sourcePosition is None or isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.AST.Element) No source position handed over!'
        assert (_scope is None or isinstance(_scope, Scope)), \
            '(PyNestML.AST.Element) Wrong type of scope handed over!'
        self.__sourcePosition = _sourcePosition
        self.__scope = _scope

    def getSourcePosition(self):
        """
        Returns the source position of the element.
        :return: an source position object.
        :rtype: ASTSourcePosition
        """
        return self.__sourcePosition

    def getScope(self):
        """
        Returns the scope of this element.
        :return: a scope object.
        :rtype: Scope 
        """
        return self.__scope

    def updateScope(self, _scope=None):
        """
        Updates the scope of this element.
        :param _scope: a scope object.
        :type _scope: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.AST.Element) No or wrong type of scope provided (%s)!' % (type(_scope))
        self.__scope = _scope
