# -*- coding: utf-8 -*-
#
# ast_node.py
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

from typing import Optional, List

from abc import ABCMeta, abstractmethod

from pynestml.symbol_table.scope import Scope

from pynestml.utils.ast_source_location import ASTSourceLocation


class ASTNode(metaclass=ABCMeta):
    """
    This class is not a part of the grammar but is used to store commonalities of all possible meta_model classes,
    e.g., the source position.

    This class is abstract, thus no instances can be created.

    Attributes:
        source_position = None
        scope = None
        comment = None
        #
        pre_comments = list()
        in_comment = None
        #
        implicit_conversion_factor = None
    """

    def __init__(self, source_position: ASTSourceLocation = None, scope: Scope = None, comment: Optional[str] = None, pre_comments: Optional[List[str]] = None,
                 in_comment: Optional[str] = None, implicit_conversion_factor: Optional[float] = None):
        """
        The standard constructor.
        :param source_position: a source position element.
        :param scope: the scope in which this element is embedded in.
        :param comment: comment for this node
        :param pre_comments: pre-comments for this node
        :param in_comment: in-comment for this node
        :param implicit_conversion_factor: see set_implicit_conversion_factor()
        """
        self.source_position = source_position
        self.scope = scope
        self.comment = comment
        if pre_comments is None:
            pre_comments = []
        self.pre_comments = pre_comments
        self.in_comment = in_comment
        self.implicit_conversion_factor = implicit_conversion_factor

    @abstractmethod
    def clone(self):
        """
        Return a deep copy of this node.
        """
        pass

    @abstractmethod
    def equals(self, other):
        """
        The equals operation.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        pass

    # todo: we can do this with a visitor instead of hard coding grammar traversals all over the place
    @abstractmethod
    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        pass

    def set_implicit_conversion_factor(self, implicit_factor: Optional[float]) -> None:
        """
        Sets a factor that, when applied to the (unit-typed) expression, converts it to the magnitude of the
        context where it is used. eg. Volt + milliVolt needs to either be
        1000*Volt + milliVolt or Volt + 0.001 * milliVolt
        :param implicit_factor: the factor to be installed
        """
        self.implicit_conversion_factor = implicit_factor

    def get_implicit_conversion_factor(self) -> Optional[float]:
        """
        Returns the factor installed as implicitConversionFactor for this expression
        :return: the conversion factor, if present, or None
        """
        return self.implicit_conversion_factor

    def get_source_position(self):
        """
        Returns the source position of the element.
        :return: a source position object.
        :rtype: ASTSourceLocation
        """
        if self.source_position is None:
            return ASTSourceLocation.get_predefined_source_position()
        return self.source_position

    def set_source_position(self, new_position):
        """
        Updates the source position of the element.
        :param new_position: a new source position
        :type new_position: ASTSourceLocation
        :return: a source position object.
        :rtype: ASTSourceLocation
        """
        self.source_position = new_position

    def get_scope(self):
        """
        Returns the scope of this element.
        :return: a scope object.
        :rtype: Scope
        """
        return self.scope

    def update_scope(self, _scope):
        """
        Updates the scope of this element.
        :param _scope: a scope object.
        :type _scope: Scope
        """
        self.scope = _scope

    def get_comment(self):
        """
        Returns the comment of this element.
        :return: a comment.
        :rtype: str
        """
        return self.comment

    def set_comment(self, comment):
        """
        Updates the comment of this element.
        :param comment: a comment
        :type comment: str
        """
        self.comment = comment

    def has_comment(self):
        """
        Indicates whether this element stores a comment.
        :return: True if has comment, otherwise False.
        :rtype: bool
        """
        return self.comment is not None and len(self.comment) > 0

    def print_comment(self, prefix: str = "") -> str:
        """
        Prints the comment of this meta_model element.
        :param prefix: a prefix string
        :return: a comment
        """
        ret = ''
        if not self.has_comment():
            return prefix if prefix is not None else ''
        # in the last part, delete the new line if it is the last comment, otherwise there is an ugly gap
        # between the comment and the element
        for comment in self.get_comment():
            ret += (prefix + ' ' if prefix is not None else '') + comment + \
                   ('\n' if self.get_comment().index(comment) < len(self.get_comment()) - 1 else '')
        return ret

    def get_comments(self):
        comments = list()
        comments.extend(self.pre_comments)
        if self.in_comment is not None:
            comments.append(self.in_comment)
        return comments

    def accept(self, visitor):
        """
        Double dispatch for visitor pattern.
        :param visitor: A visitor.
        :type visitor: Inherited from ASTVisitor.
        """
        visitor.handle(self)

    def __str__(self):
        from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
        return NESTMLPrinter().print(self)
