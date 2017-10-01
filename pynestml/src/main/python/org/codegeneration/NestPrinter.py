#
# NestPrinter.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class NestPrinter(object):
    """
    This class contains all methods as required to transform
    """
    __nestml2NESTTypeConverter = None  # todo

    def __init__(self):
        """
        Initialized the expression print
        """
        self.nestml2NESTTypeConverter = None  # todo
        return

    def printExpression(self, _ast=None):
        """
        Prints the handed over expression to a nest readable format.
        :param _ast: a single ast node.
        :type _ast: ASTExpression or ASTSimpleExpression
        :return: the corresponding string representation
        :rtype: str
        """
        return "TODO expr"

    def printMethodCall(self, _ast=None):
        """
        Prints a single handed over function call.
        :param _ast: a single function call.
        :type _ast: ASTFunctionCall
        :return: the corresponding string representation.
        :rtype: str
        """
        return "TODO function"

    def printComparisonOperator(self, _forStmt=None):
        """
        Prints a single handed over comparison operator to a Nest processable format.
        :param _ast: a single comparison operator object.
        :type _ast: ASTComparisonOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTForStmt import ASTForStmt
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        step = _forStmt.getStep()
        if step < 0:
            return '>'
        elif step > 0:
            return '<'
        else:
            return '!='  # todo, this should not happen actually

    def printVariable(self, _ast=None):
        """
        Prints a single handed over variable.
        :param _ast: a single variable
        :type _ast: ASTVariable
        :return: a string representation
        :rtype: str
        """
        return "TODO variable"

    def printStep(self, _forStmt=None):
        """
        Prints the step length to a nest processable format.
        :param _forStmt: a single for stmt
        :type _forStmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTForStmt import ASTForStmt
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        return _forStmt.getStep()

    def printOrigin(self, _variableSymbol=None):
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding prefix
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import VariableSymbol, BlockType
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        if _variableSymbol.getBlockType() == BlockType.STATE:
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.INITIAL_VALUES:  # todo
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.EQUATION:
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.PARAMETERS:
            return 'P_.'
        elif _variableSymbol.getBlockType() == BlockType.INTERNALS:
            return 'V_.'
        elif _variableSymbol.getBlockType() == BlockType.INPUT_BUFFER_CURRENT:
            return 'B_.'
        elif _variableSymbol.getBlockType() == BlockType.INPUT_BUFFER_SPIKE:
            return 'B_.'
        else:
            return ''

    def printOutputEvent(self, _astBody=None):
        """
        For the handed over neuron, this operations checks of output event shall be preformed.
        :param _astBody: a single neuron body
        :type _astBody: ASTBody
        :return: the corresponding representation of the event
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTBody import ASTBody
        assert (_astBody is not None and isinstance(_astBody, ASTBody)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of body provided (%s)!' % type(_astBody)
        outputs = _astBody.getOutputBlocks()
        if len(outputs) > 0:
            output = outputs[0]
            if outputs.isSpike():
                return 'nest::SpikeEvent'
            elif outputs.isCurrent():
                return 'nest::CurrentEvent'
            else:
                Logger.logMessage('Unexpected output type. Must be current or spike.', LOGGING_LEVEL.ERROR)
                return 'none'
        else:
            return 'none'
