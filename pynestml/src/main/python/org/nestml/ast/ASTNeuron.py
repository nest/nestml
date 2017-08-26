"""
/*
 *  ASTNeuron.py
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
from pynestml.src.main.python.org.nestml.ast.ASTBody import ASTBody


class ASTNeuron:
    """
    This class is used to store instances of neurons.
    ASTNeuron represents neuron.
    @attribute Name    The name of the neuron
    @attribute Body    The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        neuron : 'neuron' NAME body;
    """
    __name = None
    __body = None

    def __init__(self, _name=None, _body=None):
        """
        Standard constructor.
        :param _name: the name of the neuron.
        :type _name: str
        :param _body: the body containing the definitions.
        :type _body: ASTBody
        """
        self.__name = _name
        self.__body = _body

    @classmethod
    def makeASTNeuron(cls, _name=None, _body=None):
        """
        Factory method of the ASTNeuron class.
        :param _name: the name of the neuron
        :type _name: str
        :param _body: the body containing the definitions.
        :type _body: ASTBody
        :return: a new ASTNeuron object.
        :rtype: ASTNeuron
        """
        assert (_name is not None), '(NESTML.AST) No neuron name provided.'
        assert (_body is not None), '(NESTML.AST) No neuron body provided.'
        return cls(_name, _body)

    def getName(self):
        """
        Returns the name of the neuron.
        :return: the name of the neuron.
        :rtype: str
        """
        return self.__name

    def getBody(self):
        """
        Return the body of the neuron.
        :return: the body containing the definitions.
        :rtype: ASTBody
        """
        return self.__body

    def printAST(self):
        """
        Returns a string representation of the neuron.
        :return: a string representation.
        :rtype: str
        """
        return 'neuron ' + self.getName() + self.getBody().printAST()
