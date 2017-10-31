#
# ASTSourcePosition.py
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


class ASTSourcePosition(object):
    """
    This class is used to store information regarding the source position of an element.
    """
    __startLine = 0
    __startColumn = 0
    __endLine = 0
    __endColumn = 0

    def __init__(self, _startLine=0, _startColumn=0, _endLine=0, _endColumn=0):
        """
        Standard constructor.
        :param _startLine: The start line of the object
        :type _startLine: int
        :param _startColumn: The start column of the object
        :type _startColumn: int
        :param _endLine: The end line of the object
        :type _endLine: int
        :param _endColumn: The end column of the object
        :type _endColumn: int
        """
        assert (_startColumn is not None and isinstance(_startColumn, int)), \
            '(PyNestML.AST.SourcePosition) No or wrong type of start-column provided (%s)!' % type(_startColumn)
        assert (_startLine is not None and isinstance(_startLine, int)), \
            '(PyNestML.AST.SourcePosition) No or wrong type of start-line provided (%s)!' % type(_startLine)
        assert (_endColumn is not None and isinstance(_endColumn, int)), \
            '(PyNestML.AST.SourcePosition) No or wrong type of end-column provided (%s)!' % type(_endColumn)
        assert (_endLine is not None and isinstance(_endLine, int)), \
            '(PyNestML.AST.SourcePosition) No or wrong type of end-line provided (%s)!' % type(_endLine)
        self.__startLine = _startLine
        self.__startColumn = _startColumn
        self.__endLine = _endLine
        self.__endColumn = _endColumn
        return

    @classmethod
    def makeASTSourcePosition(cls, _startLine=0, _startColumn=0, _endLine=0, _endColumn=0):
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
        :rtype: ASTSourcePosition
        """
        return cls(_startLine=_startLine, _startColumn=_startColumn, _endLine=_endLine, _endColumn=_endColumn)

    def getStartLine(self):
        """
        Returns the start line of the element.
        :return: the start line as int
        :rtype: int
        """
        return self.__startLine

    def getStartColumn(self):
        """
        Returns the start column of the element.
        :return: the start column as int
        :rtype: int
        """
        return self.__startColumn

    def getEndLine(self):
        """
        Returns the end line of the element.
        :return: the end line as int
        :rtype: int
        """
        return self.__endLine

    def getEndColumn(self):
        """
        Returns the end column of the element.
        :return: the end column as int
        :rtype: int
        """
        return self.__endColumn

    def printSourcePosition(self):
        """
        Returns a string representation of the source position of this element.
        :return: a string representation
        :rtype: str
        """
        return '[' + str(self.getStartLine()) + ':' + str(self.getStartColumn()) + ';' + \
               str(self.getEndLine()) + ':' + str(self.getEndColumn()) + ']'

    def equals(self, _sourcePosition=None):
        """
        Checks if the handed over position is equal to this.
        :param _sourcePosition: a source position.
        :type _sourcePosition: ASTSourcePosition
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourcePosition):
            return False
        return self.getStartLine() == _sourcePosition.getStartLine() and \
               self.getStartColumn() == _sourcePosition.getStartColumn() and \
               self.getEndLine() == _sourcePosition.getEndLine() and \
               self.getEndColumn() == _sourcePosition.getEndColumn()

    def before(self, _sourcePosition=None):
        """
        Checks if the handed over position is smaller than this.
        :param _sourcePosition: a source position.
        :type _sourcePosition: ASTSourcePosition
        :return: True if smaller, otherwise False
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourcePosition):
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
        :rtype: ASTSourcePosition
        """
        return cls(-1, -1, -1, -1)

    @classmethod
    def getAddedSourcePosition(cls):
        """
        Returns a source position which symbolize that the corresponding element has been added by the solver.
        :return: a source position.
        :rtype: ASTSourcePosition
        """
        return cls(-2, -2, -2, -2)

    def encloses(self, _sourcePosition=None):
        """
        Checks if the handed over position is enclosed in this source position, e.g.,
            line 0 to 10 encloses lines 0 to 9 etc.
        :param _sourcePosition: a source position 
        :type _sourcePosition: ASTSourcePosition
        :return: True if enclosed, otherwise False.
        :rtype: bool
        """
        if not isinstance(_sourcePosition, ASTSourcePosition):
            return False

        if self.getStartLine() <= _sourcePosition.getStartLine() and \
                        self.getEndLine() >= _sourcePosition.getEndLine() and \
                        self.getStartColumn() <= _sourcePosition.getStartColumn() and \
                        self.getEndColumn() >= _sourcePosition.getEndColumn():
            return True
        else:
            return False
