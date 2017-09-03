"""
 /*
 *  ASTSourcePosition.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""


class ASTSourcePosition:
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
        self.__startLine = _startLine
        self.__startColumn = _startColumn
        self.__endLine = _endLine
        self.__endColumn = _endColumn

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
