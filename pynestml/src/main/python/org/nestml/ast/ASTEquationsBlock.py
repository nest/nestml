#
# ASTEquationsBlock.py
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


from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement
from pynestml.src.main.python.org.nestml.ast.ASTOdeEquation import ASTOdeEquation
from pynestml.src.main.python.org.nestml.ast.ASTOdeFunction import ASTOdeFunction
from pynestml.src.main.python.org.nestml.ast.ASTOdeShape import ASTOdeShape


class ASTEquationsBlock(ASTElement):
    """
    This class is used to store an equations block.
    ASTEquationsBlock a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeDeclaration Block with equations and differential equations.
     Grammar:
          equationsBlock:
            'equations'
            BLOCK_OPEN
              (odeFunction|odeEquation|odeShape|NEWLINE)+
            BLOCK_CLOSE;
    """
    __declarations = None

    def __init__(self, _declarations=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _declarations: a block of definitions.
        :type _declarations: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_declarations is not None and isinstance(_declarations, list)), \
            '(PyNestML.AST.EquationsBlock) No or wrong type of declarations provided (%s)!' % type(_declarations)
        for decl in _declarations:
            assert (decl is not None and (isinstance(decl, ASTOdeShape) or
                                          isinstance(decl, ASTOdeEquation) or
                                          isinstance(decl, ASTOdeFunction))), \
                '(PyNestML.AST.EquationsBlock) No or wrong type of ode-element provided (%s)' % type(decl)
        super(ASTEquationsBlock, self).__init__(_sourcePosition)
        self.__declarations = _declarations

    @classmethod
    def makeASTEquationsBlock(cls, _declarations=None, _sourcePosition=None):
        """
        Factory method of the ASTEquationsBlock class.
        :param _declarations: a block of definitions.
        :type _declarations: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTEquations object.
        :rtype: ASTEquationsBlock
        """
        return cls(_declarations, _sourcePosition)

    def getDeclarations(self):
        """
        Returns the block of definitions.
        :return: the block
        :rtype: list(ASTOdeFunction|ASTOdeEquation|ASTOdeShape)
        """
        return self.__declarations

    def printAST(self):
        """
        Returns a string representation of the equations block.
        :return: a string representing an equations block.
        :rtype: str
        """
        ret = 'equations:\n'
        for decl in self.getDeclarations():
            ret += decl.printAST() + '\n'
        return ret + 'end'
