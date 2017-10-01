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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


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
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.AST.Neuron) No  or wrong type of neuron name provided (%s)!' % type(_name)
        assert (_body is not None and isinstance(_body, ASTBody)), \
            '(PyNestML.AST.Neuron) No or wrong type of neuron body provided (%s)!' % type(_body)
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def getInitialBlocks(self):
        """
        Returns a list of all initial blocks defined in this body.
        :return: a list of initial-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTBlockWithVariables import ASTBlockWithVariables
        for elem in self.getBody().getBodyElements():
            if isinstance(elem, ASTBlockWithVariables) and elem.isInitialValues():
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def getInputBuffers(self):
        """
        Returns a list of all defined input buffers.
        :return: a list of all input buffers.
        :rtype: list(ASTInputLine)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbols = self.getScope().getSymbolsInThisScope()
        ret = list()
        for symbol in symbols:
            if symbol.getBlockType() == BlockType.INPUT_BUFFER_SPIKE or \
                            symbol.getBlockType() == BlockType.INPUT_BUFFER_CURRENT:
                ret.append(symbol)
        return ret

    def getSpikeBuffers(self):
        """
        Returns a list of all spike input buffers defined in the model.
        :return: a list of all spike input buffers
        :rtype: list(ASTInputLine)
        """
        ret = list()
        for buffer in self.getInputBuffers():
            if buffer.isSpikeBuffer():
                ret.append(buffer)
        return ret

    def getParameterSymbols(self):
        """
        Returns a list of all parameter symbol defined in the model.
        :return: a list of parameter symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbols = self.getScope().getSymbolsInThisScope()
        ret = list()
        for symbol in symbols:
            if symbol.getBlockType() == BlockType.PARAMETERS:
                ret.append(symbol)
        return ret

    def getStateSymbols(self):
        """
        Returns a list of all state symbol defined in the model.
        :return: a list of state symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbols = self.getScope().getSymbolsInThisScope()
        ret = list()
        for symbol in symbols:
            if symbol.getBlockType() == BlockType.STATE:
                ret.append(symbol)
        return ret

    def getInternalSymbols(self):
        """
        Returns a list of all internals symbol defined in the model.
        :return: a list of internals symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbols = self.getScope().getSymbolsInThisScope()
        ret = list()
        for symbol in symbols:
            if symbol.getBlockType() == BlockType.INTERNALS:
                ret.append(symbol)
        return ret

    def getODEAliases(self):
        """
        Returns a list of all equation function symbols defined in the model.
        :return: a list of equation function  symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbols = self.getScope().getSymbolsInThisScope()
        ret = list()
        for symbol in symbols:
            if symbol.getBlockType() == BlockType.EQUATION and symbol.isFunction():
                ret.append(symbol)
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
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.getBody() is _ast:
            return self
        elif self.getBody().getParent(_ast) is not None:
            return self.getBody().getParent(_ast)
        return None

    def printAST(self):
        """
        Returns a string representation of the neuron.
        :return: a string representation.
        :rtype: str
        """
        return 'neuron ' + self.getName() + ':\n' + self.getBody().printAST() + '\nend'

    def isMultisynapseSpikes(self):
        """
        Returns whether this neuron uses multi-synapse spikes.
        :return: True if multi-synaptic, otherwise False.
        :rtype: bool
        """
        buffers = self.getSpikeBuffers()
        for buffer in buffers:
            if buffer.hasIndexParameter():
                return True
        return False

    def getMultipleReceptors(self):
        """
        Returns a list of all spike buffers which are defined as inhibitory and excitatory.
        :return: a list of spike buffers variable symbols
        :rtype: list(VariableSymbol)
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
        ret = list()
        for buffer in self.getSpikeBuffers():
            if buffer.isExcitatory() and buffer.isInhibitory():
                symbol = buffer.getScope().resolveToSymbol(buffer.getName(), SymbolKind.VARIABLE)
                if symbol is not None:
                    ret.append(symbol)
                else:
                    Logger.logMessage('Could not resolve symbol!', LOGGING_LEVEL.ERROR)
        return ret

    def getParameterNonAliasSymbols(self):
        """
        Returns a list of all variable symbols representing non-function parameter variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.getParameterSymbols():
            if not param.isFunction():
                ret.append(param)
        return

    def getStateNonAliasSymbols(self):
        """
        Returns a list of all variable symbols representing non-function state variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.getStateSymbols():
            if not param.isFunction():
                ret.append(param)
        return

    def getInternalNonAliasSymbols(self):
        """
        Returns a list of all variable symbols representing non-function internal variables.
        :return: a list of variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for param in self.getInternalSymbols():
            if not param.isFunction():
                ret.append(param)
        return

    def printComment(self):
        """
        Prints the header information of this neuron.
        :return: the comment.
        :rtype: str
        """
        return 'TODO neuron comment'
