"""
/*
 *  ASTBody.py
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


class ASTBody(ASTElement):
    """
    This class is used to store the body of a neuron, an object containing all the definitions.
    ASTBody The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        body : BLOCK_OPEN
               (NEWLINE | blockWithVariables | updateBlock | equationsBlock | inputBlock | outputBlock | function)*
               BLOCK_CLOSE;        
    """
    __bodyElements = None

    def __init__(self, _bodyElements=list(), _sourcePosition=None):
        """
        Standard constructor.
        :param _bodyElements: a list of elements, e.g. variable blocks.
        :type _bodyElements: list()
        :param _sourcePosition: the position of the element in the source model
        :rtype _sourcePosition: ASTSourcePosition
        """
        super(ASTBody, self).__init__(_sourcePosition)
        self.__bodyElements = _bodyElements

    @classmethod
    def makeASTBody(cls, _bodyElements=list(), _sourcePosition=None):
        """
        Factory method of the ASTBody class.
        :param _bodyElements: a list of elements, e.g. variable blocks.
        :type _bodyElements: list()
        :param _sourcePosition: the position of the element in the source model
        :rtype _sourcePosition: ASTSourcePosition
        :return: a new body object.
        :rtype: ASTBody
        """
        return cls(_bodyElements, _sourcePosition)

    def getBodyElements(self):
        """
        Returns the list of body elements.
        :return: a list of body elements.
        :rtype: list()
        """
        return self.__bodyElements

    def getFunctions(self):
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        :rtype: list(ASTFunction)
        """
        ret = list()
        from pynestml.src.main.python.org.nestml.ast.ASTFunction import ASTFunction
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
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
        for elem in self.getBodyElements():
            if isinstance(elem, ASTOutputBlock):
                ret.append(elem)
        return ret

    def printAST(self):
        """
        Returns a string representation of the body.
        :return: a string representing the body.
        :rtype: str
        """
        ret = ''
        for elem in self.__bodyElements:
            ret += elem.printAST()
            ret += '\n'
        return ret
