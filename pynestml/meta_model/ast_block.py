#
# ast_block.py
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


class ASTBlock(ASTNode):
    """
    This class is used to store a single block of declarations, i.e., statements.
    Grammar:
        block : ( smallStmt | compoundStmt | NEWLINE )*;
    Attribute:
        stmts = None
    """

    def __init__(self, _stmts=list(), source_position=None):
        """
        Standard constructor.
        :param _stmts: a list of statements 
        :type _stmts: list(ASTSmallStmt/ASTCompoundStmt)
        :param source_position: the position of this element
        :type source_position: ASTSourceLocation
        """
        from pynestml.meta_model.ast_stmt import ASTStmt
        assert (_stmts is not None and isinstance(_stmts, list)), \
            '(PyNestML.AST.Bloc) No or wrong type of statements provided (%s)!' % type(_stmts)
        for stmt in _stmts:
            assert (stmt is not None and isinstance(stmt, ASTStmt)), \
                '(PyNestML.AST.Bloc) No or wrong type of statement provided (%s)!' % type(stmt)

        super(ASTBlock, self).__init__(source_position)
        self.stmts = _stmts

    def get_stmts(self):
        """
        Returns the list of statements.
        :return: list of stmts.
        :rtype: list(ASTSmallStmt/ASTCompoundStmt)
        """
        return self.stmts

    def add_stmt(self, stmt):
        """
        Adds a single statement to the list of statements.
        :param stmt: a statement
        :type stmt: ASTSmallStmt,ASTCompoundStmt
        """
        self.stmts.append(stmt)

    def delete_stmt(self, stmt):
        """
        Deletes the handed over statement.
        :param stmt:
        :type stmt:
        :return: True if deleted, otherwise False.
        :rtype: bool
        """
        self.stmts.remove(stmt)

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for stmt in self.get_stmts():
            if stmt is ast:
                return self
            if stmt.get_parent(ast) is not None:
                return stmt.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTBlock):
            return False
        if len(self.get_stmts()) != len(other.get_stmts()):
            return False
        my_stmt = self.get_stmts()
        your_stmts = other.get_stmts()
        for i in range(0, len(self.get_stmts())):
            if not my_stmt[i].equals(your_stmts[i]):
                return False
        return True
