# -*- coding: utf-8 -*-
#
# symbol.py
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

from enum import Enum


class Symbol(object):
    """
    This abstract class represents a super-class for all concrete symbols as stored in a symbol table.
    Attributes:
        element_reference (AST_): A reference to an AST node which defined this symbol. This has to be in the
                                    super-class, since variables as well as functions can be user defined.
        scope : The scope in which this element is stored in.
        name (str): The name of this element, e.g., V_m.
        symbol_kind (SymbolKind): The type of this symbol, i.e., either variable, function or type.
        comment (str): A text associated with this symbol, possibly originates from the source model.
    """
    __metaclass__ = ABCMeta

    def __init__(self, element_reference, scope, name, symbol_kind):
        """
        Standard constructor of the Symbol class.
        :param element_reference: an meta_model object.
        :type element_reference: ASTObject
        :param scope: the scope in which this element is embedded in.
        :type scope: Scope
        :param name: the name of the corresponding element
        :type name: str
        :type symbol_kind:
        """
        self.referenced_object = element_reference
        self.scope = scope
        self.name = name
        self.symbol_kind = symbol_kind
        self.comment = None

    def get_referenced_object(self):
        """
        Returns the referenced object.
        :return: the referenced object.
        :rtype: ASTObject
        """
        return self.referenced_object

    def get_corresponding_scope(self):
        """
        Returns the scope in which this symbol is embedded in.
        :return: a scope object.
        :rtype: Scope
        """
        return self.scope

    def get_symbol_name(self):
        """
        Returns the name of this symbol.
        :return: the name of the symbol.
        :rtype: str
        """
        return self.name

    def get_symbol_kind(self):
        """
        Returns the type of this symbol.
        :return: the type of this symbol.
        :rtype: SymbolKind
        """
        return self.symbol_kind

    def is_defined_before(self, source_position):
        """
        For a handed over source position, this method checks if this symbol has been defined before the handed
        over position.
        :param source_position: the position of a different element.
        :type source_position: ast_source_location
        :return: True, if defined before or at the source position, otherwise False.
        :rtype: bool
        """
        return self.get_referenced_object().get_source_position().before(source_position)

    def has_comment(self):
        """
        Indicates whether this symbols is commented.
        :return: True if comment is stored, otherwise False.
        :rtype: bool
        """
        return self.get_comment() is not None and len(self.get_comment())

    def get_comment(self):
        """
        Returns the comment of this symbol.
        :return: the comment.
        :rtype: list(str)
        """
        return self.comment

    def set_comment(self, comment):
        """
        Updates the comment of this element.
        :param comment: a list comment lines.
        :type comment: list(str)
        """
        self.comment = comment

    @abstractmethod
    def print_symbol(self):
        """
        Returns a string representation of this symbol.
        """
        pass


class SymbolKind(Enum):
    """
    An enumeration of all possible symbol types to make processing easier.
    """
    VARIABLE = 1
    TYPE = 2
    FUNCTION = 3
