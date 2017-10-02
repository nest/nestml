#
# CoCoAllVariablesDefined.py
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
from pynestml.src.main.python.org.nestml.visitor.ASTExpressionCollectorVisitor import ASTExpressionCollectorVisitor
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType


class CoCoAllVariablesDefined(CoCo):
    """
    This class represents a constraint condition which ensures that all elements as used in expressions have been
    previously defined.
    Not allowed:
        state:
            V_m mV = V_m + 10mV # <- recursive definition
            V_m mV = V_n # <- not defined reference
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks if this coco applies for the handed over neuron. Models which use not defined elements are not 
        correct.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.VariablesDefined) No or wrong type of neuron provided (%s)!' % type(_neuron)
        # for each variable in all expressions, check if the variable has been defined previously
        expressions = list(ASTExpressionCollectorVisitor.collectExpressionsInNeuron(_neuron))
        for expr in expressions:
            for var in expr.getVariables():
                symbol = var.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
                # first test if the symbol has been defined at least
                if symbol is None:
                    Logger.logMessage(
                        'Variable %s at %s not declared!'
                        % (var.getName(), var.getSourcePosition().printSourcePosition()), LOGGING_LEVEL.ERROR)
                # now check if it has been defined before usage, except for buffers, those are special cases
                elif not symbol.isPredefined() and symbol.getBlockType() != BlockType.INPUT_BUFFER_CURRENT and \
                                symbol.getBlockType() != BlockType.INPUT_BUFFER_SPIKE:
                    # except for parameters, those can be defined after
                    if not symbol.getReferencedObject().getSourcePosition().before(var.getSourcePosition()) and \
                                    symbol.getBlockType() != BlockType.PARAMETERS:
                        Logger.logMessage(
                            'Variable %s at %s used before declaration!'
                            % (var.getName(), var.getSourcePosition().printSourcePosition()), LOGGING_LEVEL.ERROR)
                        # now check that they are now defined recursively, e.g. V_m mV = V_m + 1
                    if symbol.getReferencedObject().getSourcePosition().encloses(var.getSourcePosition()):
                        Logger.logMessage(
                            'Variable %s at %s defined recursively!'
                            % (var.getName(), symbol.getReferencedObject().
                               getSourcePosition().printSourcePosition()), LOGGING_LEVEL.ERROR)
        return
