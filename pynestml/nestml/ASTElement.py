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
from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
from pynestml.nestml.Scope import Scope


class ASTElement(object):
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
            '(PyNestML.AST.Element) No source position provided (%s)!' % type(_sourcePosition)
        assert (_scope is None or isinstance(_scope, Scope)), \
            '(PyNestML.AST.Element) Wrong type of scope provided (%s)!' % type(_scope)
        self.__sourcePosition = _sourcePosition
        self.__scope = _scope

    def getSourcePosition(self):
        """
        Returns the source position of the element.
        :return: an source position object.
        :rtype: ASTSourcePosition
        """
        if self.__sourcePosition is not None:
            return self.__sourcePosition
        else:
            return ASTSourcePosition(_startColumn=-1, _startLine=-1, _endColumn=-1, _endLine=-1)

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
        return

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def accept(self, _visitor=None):
        """
        Double dispatch for visitor pattern.
        :param _visitor: A visitor.
        :type _visitor: Inherited from NESTMLVisitor.
        """
        from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
        assert (_visitor is not None and isinstance(_visitor, NESTMLVisitor)), \
            '(PyNestML.AST.Element) No or wrong type of visitor provided (%s)!' % type(_visitor)
        _visitor.handle(self)
        return
