"""
/*
 *  ASTInputType.py
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


class ASTInputType:
    """
    This class is used to store the type of a buffer.
    ASTInputType represents the type of the input line e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
    Grammar:
        inputType : ('inhibitory' | 'excitatory');
    """
    __isInhibitory = False
    __isExcitatory = False

    def __init__(self, _isInhibitory=False, _isExcitatory=False):
        """
        Standard constructor.
        :param _isInhibitory: is inhibitory buffer.
        :type _isInhibitory: bool
        :param _isExcitatory: is excitatory buffer.
        :type _isExcitatory: book
        """
        assert (_isExcitatory != _isInhibitory)
        self.__isExcitatory = _isExcitatory
        self.__isInhibitory = _isInhibitory

    @classmethod
    def makeASTInputType(cls, _isInhibitory=False, _isExcitatory=False):
        """
        Factory method of the ASTInputType class.
        :param _isInhibitory: is inhibitory buffer.
        :type _isInhibitory: bool
        :param _isExcitatory: is excitatory buffer.
        :type _isExcitatory: book
        :return: a new ASTInputType object.
        :rtype: ASTInputType
        """
        return cls(_isInhibitory, _isExcitatory)

    def isExcitatory(self):
        """
        Returns whether it is excitatory type.
        :return: True if excitatory, otherwise False.
        :rtype: bool
        """
        return self.__isExcitatory

    def isInhibitory(self):
        """
        Returns whether it is inhibitory type.
        :return: True if inhibitory , otherwise False.
        :rtype: bool
        """
        return self.__isInhibitory

    def printAST(self):
        """
        Returns a string representation of the input type.
        :return: a string representation.
        :rtype: str
        """
        if self.isInhibitory():
            return 'inhibitory'
        else:
            return 'excitatory'
