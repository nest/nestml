#
# ASTNode.py
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
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.Scope import Scope


class ASTNode(object):
    """
    This class is not a part of the grammar but is used to store commonalities of all possible ast classes, e.g.,
    the source position. This class is abstract, thus no instances can be created.
    """
    __metaclass__ = ABCMeta
    __sourcePosition = None
    __scope = None
    __comment = None

    def __init__(self, source_position, scope=None):
        """
        The standard constructor.
        :param source_position: a source position element.
        :type source_position: ASTSourcePosition
        :param scope: the scope in which this element is embedded in.
        :type scope: Scope
        """
        assert (source_position is None or isinstance(source_position, ASTSourcePosition)), \
            '(PyNestML.AST.Element) No source position provided (%s)!' % type(source_position)
        assert (scope is None or isinstance(scope, Scope)), \
            '(PyNestML.AST.Element) Wrong type of scope provided (%s)!' % type(scope)
        self.__sourcePosition = source_position
        self.__scope = scope
        return

    def get_source_position(self):
        """
        Returns the source position of the element.
        :return: a source position object.
        :rtype: ASTSourcePosition
        """
        if self.__sourcePosition is not None:
            return self.__sourcePosition
        else:
            return ASTSourcePosition.getPredefinedSourcePosition()

    def set_source_position(self, new_position):
        """
        Updates the source position of the element.
        :param new_position: a new source position
        :type new_position: ASTSourcePosition
        :return: a source position object.
        :rtype: ASTSourcePosition
        """
        assert (new_position is not None and isinstance(new_position, ASTSourcePosition)), \
            '(PyNestML.AST.Element) No or wrong type of source position provided (%s)!' % type(new_position)
        self.__sourcePosition = new_position
        return

    def get_scope(self):
        """
        Returns the scope of this element.
        :return: a scope object.
        :rtype: Scope 
        """
        return self.__scope

    def update_scope(self, _scope=None):
        """
        Updates the scope of this element.
        :param _scope: a scope object.
        :type _scope: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.AST.Element) No or wrong type of scope provided (%s)!' % (type(_scope))
        self.__scope = _scope
        return

    def getComment(self):
        """
        Returns the comment of this element.
        :return: a comment.
        :rtype: str
        """
        return self.__comment

    def setComment(self, _comment=None):
        """
        Updates the comment of this element.
        :param _comment: a comment
        :type _comment: str
        """
        self.__comment = _comment

    def hasComment(self):
        """
        Indicates whether this element stores a prefix.
        :return: True if has comment, otherwise False.
        :rtype: bool
        """
        return self.__comment is not None and len(self.__comment) > 0

    def printComment(self, _prefix=None):
        """
        Prints the comment of this ast element.
        :param _prefix: a prefix string
        :type _prefix: str
        :return: a comment
        :rtype: str
        """
        ret = ''
        if not self.hasComment():
            return _prefix if _prefix is not None else ''
        # in the last part, delete the new line if it is the last comment, otherwise there is an ugly gap
        # between the comment and the element
        for comment in self.getComment():
            ret += (_prefix + ' ' if _prefix is not None else '') + comment + \
                   ('\n' if self.getComment().index(comment) < len(self.getComment()) - 1 else '')
        return ret

    @abstractmethod
    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        pass

    def accept(self, _visitor=None):
        """
        Double dispatch for visitor pattern.
        :param _visitor: A visitor.
        :type _visitor: Inherited from NESTMLVisitor.
        """
        from pynestml.modelprocessor.ASTVisitor import ASTVisitor
        assert (_visitor is not None and isinstance(_visitor, ASTVisitor)), \
            '(PyNestML.AST.Element) No or wrong type of visitor provided (%s)!' % type(_visitor)
        _visitor.handle(self)
        return

    @abstractmethod
    def __str__(self):
        """
        Prints the node to a readable format.
        :return: a string representation of the node.
        :rtype: str
        """
        pass

    @abstractmethod
    def equals(self, _other=None):
        """
        The equals operation.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        pass
