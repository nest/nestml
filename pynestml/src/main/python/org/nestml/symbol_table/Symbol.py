"""
/*
 *  Symbol.py
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


class Symbol:
    """
    This class is ues to store information regarding a single symbol as required for a correct handling of scopes
    and context conditions. A single symbol is a declaration or an argument of a function.
    E.g.:   V_m mV = .... 
            function x(arg1,...)
    """
    __source_position = None
    __element_reference = None

    def __init__(self, _sourcePosition=None, _elementReference=None):
        """
        Standard constructor of the Symbol class.
        :param _sourcePosition: the source position of this symbol.
        :type _sourcePosition: ASTSourcePosition
        :param _elementReference: an ast object.
        :type _elementReference: ASTObject
        """
        self.__source_position = _sourcePosition
        self.__element_reference = _elementReference

    def getSourcePosition(self):
        """
        Returns the source position of this symbol.
        :return: the source position
        :rtype: ASTSourcePosition
        """
        return self.__source_position

    def getReferencedObject(self):
        """
        Returns the referenced object.
        :return: the referenced object.
        :rtype: ASTObject
        """
        return self.__element_reference





