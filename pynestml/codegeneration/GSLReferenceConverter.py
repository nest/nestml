#
# GSLReferenceConverter.py
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
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables


class GSLReferenceConverter(IReferenceConverter):
    """
    This class is used to convert operators and constant to the GSL (GNU Scientific Library) processable format.
    """

    __isUpperBound = None
    __maximalExponent = 10.0

    def __init__(self, _isUpperBound=False):
        """
        Standard constructor.
        :param _isUpperBound: Indicates whether an upper bound for the exponent shall be used.
        :type _isUpperBound: bool
        """
        assert (_isUpperBound is not None and isinstance(_isUpperBound, bool)), \
            '(PyNestML.CodeGeneration.GSLReferenceConverter) No or wrong type of is-upper-bound' \
            ' parameter provided (%s)!' % type(_isUpperBound)
        self.__isUpperBound = _isUpperBound
        return

    def convertNameReference(self, _astVariable):
        """
        Converts a single name reference to a gsl processable format.
        :param _astVariable: a single variable
        :type _astVariable: ASTVariable
        :return: a gsl processable format of the variable
        :rtype: str
        """
        assert (_astVariable is not None and isinstance(_astVariable, ASTVariable)), \
            '(PyNestML.CodeGeneration.GSLReferenceConverter) No or wrong type of variable provided (%s)!' % type(
                _astVariable)
        variableName = NestNamesConverter.convertToCPPName(_astVariable.getName())
        symbol = _astVariable.getScope().resolveToSymbol(_astVariable.getCompleteName(), SymbolKind.VARIABLE)

        if PredefinedUnits.isUnit(_astVariable.getCompleteName()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.getUnitIfExists(_astVariable.getCompleteName()).getUnit()))
        if symbol.isInitValues():
            return GSLNamesConverter.name(symbol)
        elif symbol.isBuffer():
            return 'node.B_.' + NestNamesConverter.bufferValue(symbol)
        elif variableName == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        elif symbol.isLocal() or symbol.isFunction():
            return variableName
        elif symbol.hasVectorParameter():
            return 'node.get_' + variableName + '()[i]'
        else:
            return 'node.get_' + variableName + '()'

    def convertFunctionCall(self, _astFunctionCall):
        """
        Converts a single function call to a gsl processable format.
        :param _astFunctionCall: a single function call
        :type _astFunctionCall: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.GSLReferenceConverter) No or wrong type of function call provided (%s)!' \
            % type(_astFunctionCall)
        functionName = _astFunctionCall.getName()
        if functionName == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        if functionName == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        if functionName == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        if functionName == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        if functionName == PredefinedFunctions.EXPM1:
            return 'numerics::expm1(%s)'
        if functionName == PredefinedFunctions.EXP:
            if self.__isUpperBound:
                return 'std::exp(std::min(%s,' + str(self.__maximalExponent) + '))'
            else:
                return 'std::exp(%s)'
        if functionName == PredefinedFunctions.MAX or functionName == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        if functionName == PredefinedFunctions.MIN or functionName == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        if functionName == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        raise UnsupportedOperationException('Cannot map the function: "' + functionName + '".')

    def convertConstant(self, _constantName):
        """
        No modifications to the constant required.
        :param _constantName: a single constant.
        :type _constantName: str
        :return: the same constant
        :rtype: str
        """
        return _constantName

    def convertUnaryOp(self, _unaryOperator):
        """
        No modifications to the operator required.
        :param _unaryOperator: a string of a unary operator.
        :type _unaryOperator: str
        :return: the same operator
        :rtype: str
        """
        return _unaryOperator

    def convertBinaryOp(self, _binaryOperator):
        """
        Converts a singe binary operator. Here, we have only to regard the pow operator in a special manner.
        :param _binaryOperator: a binary operator in string representation.
        :type _binaryOperator:  str
        :return: a string representing the included binary operator.
        :rtype: str
        """
        assert (_binaryOperator is not None and isinstance(_binaryOperator, str)), \
            '(PyNestML.CodeGeneration.GSLReferenceConverter) No or wrong type of binary operator provided (%s)!' % type(
                _binaryOperator)
        if _binaryOperator == '**':
            return 'pow(%s, %s)'
        else:
            return '(%s)' + _binaryOperator + '(%s)'

    def convertLogicalNot(self):
        return NESTReferenceConverter.convertLogicalNot()

    def convertLogicalOperator(self, _op):
        return NESTReferenceConverter.convertLogicalOperator(_op)

    def convertComparisonOperator(self, _op):
        return NESTReferenceConverter.convertComparisonOperator(_op)

    def convertBitOperator(self, _op):
        return NESTReferenceConverter.convertBitOperator(_op)

    def convertEncapsulated(self):
        return NESTReferenceConverter.convertEncapsulated()

    def convertTernaryOperator(self):
        return NESTReferenceConverter.convertTernaryOperator()

    def convertArithmeticOperator(self, _op):
        return NESTReferenceConverter.convertArithmeticOperator(_op)


class UnsupportedOperationException(Exception):
    """
    This exception is thrown whenever a operator can not be identified.
    """
    pass
