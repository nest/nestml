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
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTNeuron(ASTElement):
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

    def __init__(self, _name=None, _body=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the neuron.
        :type _name: str
        :param _body: the body containing the definitions.
        :type _body: ASTBody
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_name is not None and isinstance(_name, str)), '(PyNestML.AST.Neuron) No neuron name provided.'
        assert (_body is not None and isinstance(_body, ASTBody)), '(PyNestML.AST.Neuron) No neuron body provided.'
        super(ASTNeuron, self).__init__(_sourcePosition)
        self.__name = _name
        self.__body = _body

    @classmethod
    def makeASTNeuron(cls, _name=None, _body=None, _sourcePosition=None):
        """
        Factory method of the ASTNeuron class.
        :param _name: the name of the neuron
        :type _name: str
        :param _body: the body containing the definitions.
        :type _body: ASTBody
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTNeuron object.
        :rtype: ASTNeuron
        """
        return cls(_name, _body, _sourcePosition)

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
        return 'neuron ' + self.getName() + ':\n' + self.getBody().printAST() + '\nend'
