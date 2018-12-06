#
# ast_assignment.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_source_location import ASTSourceLocation
from pynestml.meta_model.ast_variable import ASTVariable


class ASTMagicNamespace(ASTNode):
    """
    """

    def __init__(self, namespace=None, name=None, source_position=None):
        """
        """
        super(ASTMagicNamespace, self).__init__(source_position)
        self.namespace = namespace
        self.name = name
        print("*********** CREATD ASTMagicNamespace wth " + str(name) + ", namespace= " + str(namespace))

    def get_namespace(self):
        """
        Returns the left-hand side variable.
        :return: left-hand side variable object.
        :rtype: ASTVariable
        """
        return self.namespace

    def get_name(self):
        """
        Returns the right-hand side rhs.
        :return: rhs object.
        :rtype: ast_expression
        """
        return self.name

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_name() is ast:
            return self
        elif self.get_namespace() is ast:
            return self
        return None

    def equals(self, other):
        """
        The equals operation.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTMagicNamespace):
            return False
        return (self.get_name().equals(other.get_name()) and
                self.get_namespace().equals(other.get_namespace()))
