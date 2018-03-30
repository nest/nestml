#
# ASTStmt.py
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
from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt


class ASTStmt(ASTNode):
    """
    Stores a reference to either small or compound statement.
    """
    small_stmt = None
    compound_stmt = None

    def __init__(self, small_stmt, compound_stmt, source_position):
        # type: (ASTSmallStmt,ASTCompoundStmt) -> None
        super(ASTStmt, self).__init__(source_position)
        self.small_stmt = small_stmt
        self.compound_stmt = compound_stmt

    def getParent(self, _ast=None):
        """
        Returns the parent node of a handed over AST object.
        """
        # type: ASTNode -> ASTNode
        if self.small_stmt is _ast:
            return self
        elif self.small_stmt is not None and self.small_stmt.getParent(_ast) is not None:
            return self.small_stmt.getParent(_ast)
        if self.compound_stmt is _ast:
            return self
        elif self.compound_stmt is not None and self.compound_stmt.getParent(_ast) is not None:
            return self.compound_stmt.getParent(_ast)

    def __str__(self):
        if self.is_small_stmt():
            return str(self.small_stmt)
        else:
            return str(self.compound_stmt)

    def is_small_stmt(self):
        return self.small_stmt is not None

    def is_compound_stmt(self):
        return self.compound_stmt is not None

    def equals(self, _other=None):
        if not isinstance(_other, ASTStmt):
            return False
        return self.small_stmt.equals(_other.small_stmt) and self.compound_stmt.equals(_other.compound_stmt)
