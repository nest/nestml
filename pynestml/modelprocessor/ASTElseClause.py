#
# ASTElseClause.py
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
from pynestml.modelprocessor.ASTBlock import ASTBlock


class ASTElseClause(ASTNode):
    """
    This class is used to store a single else-clause.
    Grammar:
        elseClause : 'else' BLOCK_OPEN block;
    """
    __block = None

    def __init__(self, _block=None, source_position=None):
        """
        Standard constructor.
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param source_position: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.AST.ElseClause) No or wrong type of block provided (%s)!' % type(_block)
        super(ASTElseClause, self).__init__(source_position)
        self.__block = _block

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.getBlock() is _ast:
            return self
        elif self.getBlock().getParent(_ast) is not None:
            return self.getBlock().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the else clause.
        :return: a string representation of the else clause.
        :rtype: str
        """
        return 'else:\n' + str(self.getBlock())

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTElseClause):
            return False
        return self.getBlock().equals(_other.getBlock())
