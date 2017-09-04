"""
 /*
 *  ASTElement.py
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
from abc import ABCMeta
from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition


class ASTElement:
    """
    This class is not a part of the grammar but is used to store commonalities of all possible ast classes, e.g.,
    the source position. This class is abstract, thus no instances can be created.
    """
    __metaclass__ = ABCMeta
    __sourcePosition = None

    def __init__(self, _sourcePosition=None):
        """
        The standard constructor.
        :param _sourcePosition: a source position element.
        :type _sourcePosition: ASTSourcePosition
        """
        assert (_sourcePosition is None or isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.AST) No source position handed over!'
        self.__sourcePosition = _sourcePosition

    def getSourcePosition(self):
        """
        Returns the source position of the element.
        :return: an source position object.
        :rtype: ASTSourcePosition
        """
        return self.__sourcePosition
