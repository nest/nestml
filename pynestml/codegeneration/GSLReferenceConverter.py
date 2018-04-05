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
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Symbol import SymbolKind


class GSLReferenceConverter(IReferenceConverter):
    """
    This class is used to convert operators and constant to the GSL (GNU Scientific Library) processable format.
    """

    is_upper_bound = None
    maximal_exponent = 10.0

    def __init__(self, is_upper_bound=False):
        """
        Standard constructor.
        :param is_upper_bound: Indicates whether an upper bound for the exponent shall be used.
        :type is_upper_bound: bool
        """
        self.is_upper_bound = is_upper_bound

    def convertNameReference(self, ast_variable):
        """
        Converts a single name reference to a gsl processable format.
        :param ast_variable: a single variable
        :type ast_variable: ASTVariable
        :return: a gsl processable format of the variable
        :rtype: str
        """
        variable_name = NestNamesConverter.convertToCPPName(ast_variable.get_name())
        symbol = ast_variable.get_scope().resolve_to_symbol(ast_variable.get_complete_name(), SymbolKind.VARIABLE)

        if PredefinedUnits.is_unit(ast_variable.get_complete_name()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.get_unit(ast_variable.get_complete_name()).get_unit()))
        if symbol.is_init_values():
            return GSLNamesConverter.name(symbol)
        elif symbol.is_buffer():
            return 'node.B_.' + NestNamesConverter.bufferValue(symbol)
        elif variable_name == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        elif symbol.is_local() or symbol.is_function():
            return variable_name
        elif symbol.has_vector_parameter():
            return 'node.get_' + variable_name + '()[i]'
        else:
            return 'node.get_' + variable_name + '()'

    def convertFunctionCall(self, ast_function_call):
        """
        Converts a single function call to a gsl processable format.
        :param ast_function_call: a single function call
        :type ast_function_call: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        function_name = ast_function_call.get_name()
        if function_name == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        if function_name == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        if function_name == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        if function_name == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        if function_name == PredefinedFunctions.EXPM1:
            return 'numerics::expm1(%s)'
        if function_name == PredefinedFunctions.EXP:
            if self.is_upper_bound:
                return 'std::exp(std::min(%s,' + str(self.maximal_exponent) + '))'
            else:
                return 'std::exp(%s)'
        if function_name == PredefinedFunctions.MAX or function_name == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        if function_name == PredefinedFunctions.MIN or function_name == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        raise UnsupportedOperationException('Cannot map the function: "' + function_name + '".')

    def convertConstant(self, constant_name):
        """
        No modifications to the constant required.
        :param constant_name: a single constant.
        :type constant_name: str
        :return: the same constant
        :rtype: str
        """
        return constant_name

    def convertUnaryOp(self, unary_operator):
        """
        No modifications to the operator required.
        :param unary_operator: a string of a unary operator.
        :type unary_operator: str
        :return: the same operator
        :rtype: str
        """
        return str(unary_operator) + '(%s)'

    def convertBinaryOp(self, binary_operator):
        """
        Converts a singe binary operator. Here, we have only to regard the pow operator in a special manner.
        :param binary_operator: a binary operator in string representation.
        :type binary_operator:  str
        :return: a string representing the included binary operator.
        :rtype: str
        """
        from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
        if isinstance(binary_operator, ASTArithmeticOperator) and binary_operator.is_pow_op:
            return 'pow(%s, %s)'
        else:
            return '%s' + str(binary_operator) + '%s'

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
