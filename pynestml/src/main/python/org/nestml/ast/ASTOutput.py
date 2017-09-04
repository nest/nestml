"""
/*
 *  ASTOutput.py
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
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTOutput(ASTElement):
    """
    This class is used to store output buffer declarations.
    ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    Grammar:
        outputBuffer: 'output' BLOCK_OPEN ('spike' | 'current') ;
    """
    __type = None

    def __init__(self, _type=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _type: the type of the output buffer.
        :type _type: str
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_type is 'spike' or _type is _type is 'current'), \
            '(PyNestML) Wrong type (=%s) of buffer provided!' % _type
        super(ASTOutput, self).__init__(_sourcePosition)
        self.__type = _type

    @classmethod
    def makeASTOutput(cls, _type=None, _sourcePosition=None):
        """
        Factory method of the ASTOutput class.
        :param _type: the type of the output buffer.
        :type _type: str
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTOutput object
        :rtype: ASTOutput
        """
        return cls(_type, _sourcePosition)

    def isSpike(self):
        """
        Returns whether it is a spike buffer or not.
        :return: True if spike, otherwise False.
        :rtype: bool
        """
        return self.__type is 'spike'

    def isCurrent(self):
        """
        Returns whether it is a current buffer or not.
        :return: True if current, otherwise False.
        :rtype: bool
        """
        return self.__type is 'current'

    def printAST(self):
        """
        Returns a string representation of the output declaration.
        :return: a string representation
        :rtype: str
        """
        return 'output: ' + ('spike' if self.isSpike() else 'current') + '\n'
