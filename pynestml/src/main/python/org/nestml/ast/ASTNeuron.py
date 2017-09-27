#
# ASTNeuron.py
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

    def getFunctions(self):
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        :rtype: list(ASTFunction)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTFunction import ASTFunction
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTFunction):
                ret.append(elem)
        return ret

    def getUpdateBlocks(self):
        """
        Returns a list of all update blocks defined in this body.
        :return: a list of update-block elements.
        :rtype: list(ASTUpdateBlock)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTUpdateBlock import ASTUpdateBlock
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTUpdateBlock):
                ret.append(elem)
        return ret

    def getStateBlocks(self):
        """
        Returns a list of all state blocks defined in this body.
        :return: a list of state-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTBlockWithVariables) and elem.isState():
                ret.append(elem)
        return ret

    def getParameterBlocks(self):
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTBlockWithVariables) and elem.isParameters():
                ret.append(elem)
        return ret

    def getInternalsBlocks(self):
        """
        Returns a list of all internals blocks defined in this body.
        :return: a list of internals-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTBlockWithVariables) and elem.isInternals():
                ret.append(elem)
        return ret

    def getEquationsBlocks(self):
        """
        Returns a list of all equations blocks defined in this body.
        :return: a list of equations-blocks.
        :rtype: list(ASTEquationsBlock)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTEquationsBlock import ASTEquationsBlock
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTEquationsBlock):
                ret.append(elem)
        return ret

    def getInputBlocks(self):
        """
        Returns a list of all input-blocks defined.
        :return: a list of defined input-blocks.
        :rtype: list(ASTInputBlock)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTInputBlock import ASTInputBlock
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTInputBlock):
                ret.append(elem)
        return ret

    def getOutputBlocks(self):
        """
        Returns a list of all output-blocks defined.
        :return: a list of defined output-blocks.
        :rtype: list(ASTOutputBlock)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTOutputBlock import ASTOutputBlock
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTOutputBlock):
                ret.append(elem)
        return ret

    def printAST(self):
        """
        Returns a string representation of the neuron.
        :return: a string representation.
        :rtype: str
        """
        return 'neuron ' + self.getName() + ':\n' + self.getBody().printAST() + '\nend'
