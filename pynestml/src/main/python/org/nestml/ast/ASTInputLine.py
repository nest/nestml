"""
 /*
 *  ASTInputLine.py
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


class ASTInputLine:
    """
    This class is used to store a declaration of an input line.
    ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike

    @attribute sizeParameter Optional parameter representing  multisynapse neuron.
    @attribute sizeParameter Type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute spike true iff the neuron is a spike.
    @attribute current true iff. the neuron is a current.
    Grammar:
          inputLine :
                NAME
                ('[' sizeParameter=NAME ']')?
                '<-' inputType*
                ('spike' | 'current');
    """
    __name = None
    __sizeParameter = None
    __inputTypes = None
    __isSpike = False
    __isCurrent = False

    def __init__(self, _name=None, _sizeParameter=None, _inputTypes=list(), _isSpike=False, _isCurrent=False):
        """
        Standard constructor.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _isSpike: is a spike buffer
        :type _isSpike: bool
        :param _isCurrent: is a current buffer
        :type _isCurrent: bool
        """
        assert (_name is not None)
        assert (_isSpike != _isCurrent)
        self.__isCurrent = _isCurrent
        self.__isSpike = _isSpike
        self.__inputTypes = _inputTypes
        self.__sizeParameter = _sizeParameter
        self.__name = _name

    @classmethod
    def makeASTInputLine(cls, _name=None, _sizeParameter=None, _inputTypes=list(), _isSpike=False, _isCurrent=False):
        """
        Factory method of the ASTInputLine class.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _isSpike: is a spike buffer
        :type _isSpike: bool
        :param _isCurrent: is a current buffer
        :type _isCurrent: bool
        :return: a new ASTInputLine object.
        :rtype: ASTInputLine
        """
        return cls(_name, _sizeParameter, _inputTypes, _isSpike, _isCurrent)

    def getName(self):
        """
        Returns the name of the declared buffer.
        :return: the name.
        :rtype: str
        """
        return self.__name

    def hasIndexParameter(self):
        """
        Returns whether a index parameter has been defined.
        :return: True if index has been used, otherwise False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def getIndexParameter(self):
        """
        Returns the index parameter.
        :return: the index parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def hasInputTypes(self):
        """
        Returns whether input types have been defined.
        :return: True, if at least one input type has been defined.
        :rtype: bool
        """
        return len(self.__inputTypes) > 0

    def getInputTypes(self):
        """
        Returns the list of input types.
        :return: a list of input types.
        :rtype: list(ASTInputType)
        """
        return self.__inputTypes

    def isSpike(self):
        """
        Returns whether this is a spike buffer or not.
        :return: True if spike buffer, False else.
        :rtype: bool 
        """
        return self.__isSpike

    def isSCurrent(self):
        """
        Returns whether this is a current buffer or not.
        :return: True if current buffer, False else.
        :rtype: bool 
        """
        return self.__isCurrent

    def printAST(self):
        """
        Returns a string representation of the input line.
        :return: a string representing the input line.
        :rtype: str
        """
        ret = self.getName()
        if self.hasIndexParameter():
            ret += '[' + self.getIndexParameter().printAST() + ']'
        ret += '<-'
        if self.hasIndexParameter():
            for iType in self.getInputTypes():
                ret += iType.printAST() + ' '
        if self.isSpike():
            ret += 'spike'
        else:
            ret += 'current'
        return ret
