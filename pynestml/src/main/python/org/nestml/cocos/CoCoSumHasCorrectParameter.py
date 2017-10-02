#
# CoCoSumHasCorrectParameter.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.ast.ASTSimpleExpression import ASTSimpleExpression


class CoCoSumHasCorrectParameter(CoCo):
    """
    This coco ensures that cur_sum,cond_sum and convolve get only simple variable references as inputs.
    Not allowed:
     V mV = convolve(g_in+g_ex,Buffer)
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.getName()
        visitor = SumIsCorrectVisitor()
        _neuron.accept(visitor)
        return


class SumIsCorrectVisitor(NESTMLVisitor):
    """
    This visitor ensures that sums/convolve are provided with a correct expression.
    """

    def visitFunctionCall(self, _functionCall=None):
        """
        Checks the coco on the current function call.
        :param _functionCall: a single function call.
        :type _functionCall: ASTFunctionCall
        """
        fName = _functionCall.getName()
        if fName == 'cur_sum' or fName == 'cond_sum' or fName == 'convolve':
            for arg in _functionCall.getArgs():
                if not isinstance(arg, ASTSimpleExpression) or not arg.isVariable():
                    Logger.logMessage('Argument %s of "%s"  at %s not a variable!'
                                      % (arg.printAST(), fName,
                                         _functionCall.getSourcePosition().printSourcePosition()),
                                      LOGGING_LEVEL.ERROR)
        return
