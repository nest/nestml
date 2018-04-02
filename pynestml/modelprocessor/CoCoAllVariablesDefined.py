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


from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTExpressionCollectorVisitor import ASTExpressionCollectorVisitor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.VariableSymbol import BlockType


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
    def check_co_co(cls, node=None):
        """
        Checks if this coco applies for the handed over neuron. Models which use not defined elements are not 
        correct.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.VariablesDefined) No or wrong type of neuron provided (%s)!' % type(node)
        # for each variable in all expressions, check if the variable has been defined previously
        expressions = list(ASTExpressionCollectorVisitor.collectExpressionsInNeuron(node))
        for expr in expressions:
            for var in expr.get_variables():
                symbol = var.get_scope().resolveToSymbol(var.get_complete_name(), SymbolKind.VARIABLE)
                # first test if the symbol has been defined at least
                if symbol is None:
                    code, message = Messages.getNoVariableFound(var.get_name())
                    Logger.logMessage(_neuron=node, _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR,
                                      _errorPosition=var.get_source_position())
                # now check if it has been defined before usage, except for buffers, those are special cases
                elif (not symbol.is_predefined() and symbol.get_block_type() != BlockType.INPUT_BUFFER_CURRENT and
                      symbol.get_block_type() != BlockType.INPUT_BUFFER_SPIKE):
                    # except for parameters, those can be defined after
                    if not symbol.get_referenced_object().get_source_position().before(var.get_source_position()) and \
                            symbol.get_block_type() != BlockType.PARAMETERS:
                        code, message = Messages.getVariableUsedBeforeDeclaration(var.get_name())
                        Logger.logMessage(_neuron=node, _message=message, _errorPosition=var.get_source_position(),
                                          _code=code, _logLevel=LOGGING_LEVEL.ERROR)
                        # now check that they are now defined recursively, e.g. V_m mV = V_m + 1
                    if symbol.get_referenced_object().get_source_position().encloses(var.get_source_position()) and not \
                            symbol.get_referenced_object().get_source_position().isAddedSourcePosition():
                        code, message = Messages.getVariableDefinedRecursively(var.get_name())
                        Logger.logMessage(_code=code, _message=message, _errorPosition=symbol.get_referenced_object().
                                          get_source_position(), _logLevel=LOGGING_LEVEL.ERROR, _neuron=node)
        return
