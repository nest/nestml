#
# CoCoShapeVarInCorrectExpression.py
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
from pynestml.src.main.python.org.nestml.visitor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind


class CoCoConvolveCondCorrectlyBuilt(CoCo):
    """
    This coco ensures that convolve and cond/curr sum are correctly build, i.e.,
    that the first argument is the variable from the initial block and the second argument an input buffer.
    Allowed:
        function I_syn_exc pA =   convolve(g_ex, spikesExc) * ( V_bounded - E_ex )
    Not allowed:
        function I_syn_exc pA =   convolve(g_ex, g_ex) * ( V_bounded - E_ex )

    """
    __neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node it checks if the coco applies.
        :param _ast: a single ast node
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall

        if isinstance(_ast, ASTFunctionCall) and (_ast.getName() == 'convolve' or _ast.getName() == 'cond_sum'
                                                  or _ast.getName() == 'curr_sum'):
            funcName = _ast.getName()
            symbolVar = _ast.getScope().resolveToSymbol(_ast.getArgs()[0].printAST(), SymbolKind.VARIABLE)
            symbolBuffer = _ast.getScope().resolveToSymbol(_ast.getArgs()[1].printAST(), SymbolKind.VARIABLE)
            if symbolVar is not None and not symbolVar.isShape() and not symbolVar.isInitValues():
                Logger.logMessage(
                    '[' + cls.__neuronName + '.nestml] First argument of %s at %s not a shape or equation!'
                    % (funcName, _ast.getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)
            if symbolBuffer is not None and not symbolBuffer.isInputBufferSpike():
                Logger.logMessage(
                    '[' + cls.__neuronName + '.nestml] Second argument of %s at %s not a buffer!'
                    % (funcName, _ast.getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)
        return
