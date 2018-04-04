#
# ASTSourceLocation.py
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
import sys


class ASTSourceLocation(object):
    """
    This class is used to store information regarding the source position of an element.
    """
    start_line = 0
    start_column = 0
    end_line = 0
    end_column = 0

    def __init__(self, start_line=0, start_column=0, end_line=0, end_column=0):
        """
        Standard constructor.
        :param start_line: The start line of the object
        :type start_line: int
        :param start_column: The start column of the object
        :type start_column: int
        :param end_line: The end line of the object
        :type end_line: int
        :param end_column: The end column of the object
        :type end_column: int
        """
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    @classmethod
    def make_ast_source_position(cls, _startLine=0, _startColumn=0, _endLine=0, _endColumn=0):
        """
        Factory method of the ASTSourcePosition class.
        :param _startLine: The start line of the object
        :type _startLine: int
        :param _startColumn: The start column of the object
        :type _startColumn: int
        :param _endLine: The end line of the object
        :type _endLine: int
        :param _endColumn: The end column of the object
        :type _endColumn: int
        :return: a new ASTSourcePosition object
        :rtype: ASTSourceLocation
        """
        return cls(_startLine=_startLine, _startColumn=_startColumn, _endLine=_endLine, _endColumn=_endColumn)

    def getStartLine(self):
        """
        Returns the start line of the element.
        :return: the start line as int
        :rtype: int
        """
        return self.start_line

    def getStartColumn(self):
        """
        Returns the start column of the element.
        :return: the start column as int
        :rtype: int
        """
        return self.start_column

    def getEndLine(self):
        """
        Returns the end line of the element.
        :return: the end line as int
        :rtype: int
        """
        return self.end_line

    def getEndColumn(self):
        """
        Returns the end column of the element.
        :return: the end column as int
        :rtype: int
        """
        return self.end_column

    def equals(self, _sourcePosition=None):
        """
        Checks if the handed over position is equal to this.
        :param _sourcePosition: a source position.
        :type _sourcePosition: ASTSourceLocation
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourceLocation):
            return False
        return self.getStartLine() == _sourcePosition.getStartLine() and \
               self.getStartColumn() == _sourcePosition.getStartColumn() and \
               self.getEndLine() == _sourcePosition.getEndLine() and \
               self.getEndColumn() == _sourcePosition.getEndColumn()

    def before(self, _sourcePosition=None):
        """
        Checks if the handed over position is smaller than this.
        :param _sourcePosition: a source position.
        :type _sourcePosition: ASTSourceLocation
        :return: True if smaller, otherwise False
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourceLocation):
            return False
        # in th case that it is artificially added or that it is predefined, the rule for before does not apply
        # here we assume that the insertion is added at a correct point.
        # If both are predefined, then there is no conflict
        if self.isPredefinedSourcePosition() and _sourcePosition.isPredefinedSourcePosition():
            return True
        # IF both are artificial, then its also ok
        if self.isAddedSourcePosition() and _sourcePosition.isAddedSourcePosition():
            return True
        # Predefined are always added at the beginning,
        if self.isPredefinedSourcePosition():
            return True
        if self.isAddedSourcePosition():
            return False
        if self.getStartLine() < _sourcePosition.getStartLine():
            return True
        elif self.getStartLine() == _sourcePosition.getStartLine() and \
                self.getStartColumn() < _sourcePosition.getStartColumn():
            return True
        else:
            return False

    @classmethod
    def getPredefinedSourcePosition(cls):
        """
        Returns a source position which symbolizes that the corresponding element is predefined.
        :return: a source position
        :rtype: ASTSourceLocation
        """
        return cls(-1, -1, -1, -1)

    @classmethod
    def getAddedSourcePosition(cls):
        """
        Returns a source position which symbolize that the corresponding element has been added by the solver.
        :return: a source position.
        :rtype: ASTSourceLocation
        """
        return cls(sys.maxsize, sys.maxsize, sys.maxsize, sys.maxsize)

    def isPredefinedSourcePosition(self):
        """
        Indicates whether this represents a predefined source position.
        :return: True if predefined, otherwise False.
        :rtype: bool
        """
        return self.equals(ASTSourceLocation.getPredefinedSourcePosition())

    def isAddedSourcePosition(self):
        """
        Indicates whether this represents an artificially added source position..
        :return: a source position.
        :rtype: ASTSourceLocation
        """
        return self.equals(ASTSourceLocation.getAddedSourcePosition())

    def encloses(self, _sourcePosition=None):
        """
        Checks if the handed over position is enclosed in this source position, e.g.,
            line 0 to 10 encloses lines 0 to 9 etc.
        :param _sourcePosition: a source position 
        :type _sourcePosition: ASTSourceLocation
        :return: True if enclosed, otherwise False.
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourceLocation):
            return False

        if self.getStartLine() <= _sourcePosition.getStartLine() and \
                self.getEndLine() >= _sourcePosition.getEndLine() and \
                self.getStartColumn() <= _sourcePosition.getStartColumn() and \
                self.getEndColumn() >= _sourcePosition.getEndColumn():
            return True
        else:
            return False

    def __str__(self):
        """
        A string representation of this source position.
        :return: a string representation
        :rtype: str
        """
        if self.isAddedSourcePosition():
            return '<ADDED_BY_SOLVER>'
        elif self.isPredefinedSourcePosition():
            return '<PREDEFINED>'
        else:
            return '[' + str(self.getStartLine()) + ':' + str(self.getStartColumn()) + ';' + \
                   str(self.getEndLine()) + ':' + str(self.getEndColumn()) + ']'
