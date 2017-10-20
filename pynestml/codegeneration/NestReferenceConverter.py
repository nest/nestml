#
# NESTReferenceConverter.py
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
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
from pynestml.nestml.ASTVariable import ASTVariable
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class NESTReferenceConverter(IReferenceConverter):
    """
    This concrete reference converter is used to transfer internal names to counter-pieces in NEST.
    """
    __usesGSL = False

    def __init__(self, _usesGSL=False):
        """
        Standard constructor.
        :param _usesGSL: indicates whether GSL is used.
        :type _usesGSL: bool
        """
        assert (_usesGSL is not None and isinstance(_usesGSL, bool)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _usesGSL)
        self.__usesGSL = _usesGSL
        return

    def convertBinaryOp(self, _binaryOperator):
        """
        Converts a single binary operator to nest processable format.
        :param _binaryOperator: a single binary operator string.
        :type _binaryOperator: str
        :return: the corresponding nest representation
        :rtype: str
        """
        if _binaryOperator == '**':
            return 'pow(%s, %s)'
        elif _binaryOperator == 'and':
            return '(%s) && (%s)'
        elif _binaryOperator == 'or':
            return '(%s) || (%s)'
        else:
            return '(%s)' + _binaryOperator + '(%s)'

    def convertFunctionCall(self, _astFunctionCall):
        """
        Converts a single handed over function call to nest processable format.
        :param _astFunctionCall: a single function call
        :type _astFunctionCall:  ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _astFunctionCall)
        functionName = _astFunctionCall.getName()
        if functionName == 'and':
            return '&&'
        elif functionName == 'or':
            return '||'
        elif functionName == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        elif functionName == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        elif functionName == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        elif functionName == PredefinedFunctions.MAX or functionName == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        elif functionName == PredefinedFunctions.MIN or functionName == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        elif functionName == PredefinedFunctions.EXP:
            return 'std::exp(%s)'
        elif functionName == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        elif functionName == 'expm1':
            return 'numerics::expm1(%s)'
        elif functionName == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        elif self.needsArguments(_astFunctionCall):
            return functionName + '(%s)'
        else:
            return functionName + '()'

    def convertNameReference(self, _astVariable):
        """
        Converts a single variable to nest processable format.
        :param _astVariable: a single variable.
        :type _astVariable: ASTVariable
        :return: a nest processable format.
        :rtype: str
        """
        from pynestml.codegeneration.NestPrinter import NestPrinter
        assert (_astVariable is not None and isinstance(_astVariable, ASTVariable)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _astVariable)
        variableName = NestNamesConverter.convertToCPPName(_astVariable.getCompleteName())
        # todo stesp
        if variableName == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        else:
            symbol = _astVariable.getScope().resolveToSymbol(variableName, SymbolKind.VARIABLE)
            if symbol is None:
                # this actually not happen, but an error message is better that exception
                code,message = Messages.getCouldNotResolve(variableName)
                Logger.logMessage(_logLevel=LOGGING_LEVEL.ERROR,_code=code,_message=message,
                                  _errorPosition=_astVariable.getSourcePosition())
                return ''
            else:
                if symbol.isLocal():
                    return variableName + ('[i]' if symbol.hasVectorParameter() else '')
                elif symbol.isBuffer():
                    return NestPrinter.printOrigin(symbol) + NestNamesConverter.bufferValue(symbol) \
                           + ('[i]' if symbol.hasVectorParameter() else '')
                else:
                    if symbol.isFunction():
                        return 'get_' + variableName + '()' + ('[i]' if symbol.hasVectorParameter() else '')
                    else:
                        if symbol.isInitValues():
                            return NestPrinter.printOrigin(symbol) + \
                                   (GSLNamesConverter.name(symbol)
                                    if self.__usesGSL else NestNamesConverter.name(symbol)) + \
                                   ('[i]' if symbol.hasVectorParameter() else '')
                        else:
                            return NestPrinter.printOrigin(symbol) + \
                                   NestNamesConverter.name(symbol) + \
                                   ('[i]' if symbol.hasVectorParameter() else '')

    def convertConstant(self, _constantName):
        """
        Converts a single handed over constant.
        :param _constantName: a constant as string.
        :type _constantName: str
        :return: the corresponding nest representation
        :rtype: str
        """
        if _constantName == 'inf':
            return 'std::numeric_limits<double_t>::infinity()'
        else:
            return _constantName

    def convertUnaryOp(self, _unaryOperator):
        """
        No modifications needed, thus the same operator returned.
        :param _unaryOperator: a single operator.
        :type _unaryOperator:  str
        :return: the same operator
        :rtype: str
        """
        return _unaryOperator
