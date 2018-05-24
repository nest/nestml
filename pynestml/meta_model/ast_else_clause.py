#
# ast_else_clause.py
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


class ASTElseClause(ASTNode):
    """
    This class is used to store a single else-clause.
    Grammar:
        elseClause : 'else' BLOCK_OPEN block;
    Attributes:
        block = None
    """

    def __init__(self, block, source_position):
        """
        Standard constructor.
        :param block: a block of statements.
        :type block: ast_block
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTElseClause, self).__init__(source_position)
        self.block = block

    def get_block(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ast_block
        """
        return self.block

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_block() is ast:
            return self
        elif self.get_block().get_parent(ast) is not None:
            return self.get_block().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTElseClause):
            return False
        return self.get_block().equals(other.get_block())
