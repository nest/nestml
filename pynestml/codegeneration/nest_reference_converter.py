#
# nest_reference_converter.py
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

from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.unit_converter import UnitConverter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class NESTReferenceConverter(IReferenceConverter):
    """
    This concrete reference converter is used to transfer internal names to counter-pieces in NEST.
    """

    def __init__(self, uses_gsl=False):
        """
        Standard constructor.
        :param uses_gsl: indicates whether GSL is used.
        :type uses_gsl: bool
        """
        self.uses_gsl = uses_gsl
        return

    @classmethod
    def convert_binary_op(cls, binary_operator):
        """
        Converts a single binary operator to nest processable format.
        :param binary_operator: a single binary operator string.
        :type binary_operator: AST_
        :return: the corresponding nest representation
        :rtype: str
        """
        if isinstance(binary_operator, ASTArithmeticOperator):
            return cls.convert_arithmetic_operator(binary_operator)
        if isinstance(binary_operator, ASTBitOperator):
            return cls.convert_bit_operator(binary_operator)
        if isinstance(binary_operator, ASTComparisonOperator):
            return cls.convert_comparison_operator(binary_operator)
        if isinstance(binary_operator, ASTLogicalOperator):
            return cls.convert_logical_operator(binary_operator)
        else:
            raise RuntimeError('Cannot determine binary operator!')

    @classmethod
    def convert_function_call(cls, function_call):
        """
        Converts a single handed over function call to nest processable format.
        :param function_call: a single function call
        :type function_call:  ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        function_name = function_call.get_name()
        if function_name == 'and':
            return '&&'
        elif function_name == 'or':
            return '||'
        elif function_name == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        elif function_name == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        elif function_name == PredefinedFunctions.POW:
            return 'std::pow(%s, %s)'
        elif function_name == PredefinedFunctions.MAX or function_name == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s, %s)'
        elif function_name == PredefinedFunctions.MIN or function_name == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s, %s)'
        elif function_name == PredefinedFunctions.EXP:
            return 'std::exp(%s)'
        elif function_name == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        elif function_name == 'expm1':
            return 'numerics::expm1(%s)'
        elif function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        elif ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return function_name + '(' + ', '.join(['%s' for _ in range(n_args)]) + ')'
        else:
            return function_name + '()'

    def convert_name_reference(self, variable):
        """
        Converts a single variable to nest processable format.
        :param variable: a single variable.
        :type variable: ASTVariable
        :return: a nest processable format.
        :rtype: str
        """
        from pynestml.codegeneration.nest_printer import NestPrinter
        assert (variable is not None and isinstance(variable, ASTVariable)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                variable)
        variable_name = NestNamesConverter.convert_to_cpp_name(variable.get_complete_name())

        if variable_name == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        else:
            symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
            if symbol is None:
                # this should actually not happen, but an error message is better than an exception
                code, message = Messages.get_could_not_resolve(variable_name)
                Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                                   error_position=variable.get_source_position())
                return ''
            else:
                if symbol.is_local():
                    return variable_name + ('[i]' if symbol.has_vector_parameter() else '')
                elif symbol.is_buffer():
                    return NestPrinter.print_origin(symbol) + NestNamesConverter.buffer_value(symbol) \
                           + ('[i]' if symbol.has_vector_parameter() else '')
                else:
                    if symbol.is_function:
                        return 'get_' + variable_name + '()' + ('[i]' if symbol.has_vector_parameter() else '')
                    else:
                        if symbol.is_init_values():
                            temp = NestPrinter.print_origin(symbol)
                            if self.uses_gsl:
                                temp += GSLNamesConverter.name(symbol)
                            else:
                                temp += NestNamesConverter.name(symbol)
                            temp += ('[i]' if symbol.has_vector_parameter() else '')
                            return temp
                        else:
                            return NestPrinter.print_origin(symbol) + \
                                   NestNamesConverter.name(symbol) + \
                                   ('[i]' if symbol.has_vector_parameter() else '')

    @classmethod
    def convert_constant(cls, constant_name):
        """
        Converts a single handed over constant.
        :param constant_name: a constant as string.
        :type constant_name: str
        :return: the corresponding nest representation
        :rtype: str
        """
        if constant_name == 'inf':
            return 'std::numeric_limits<double_t>::infinity()'
        else:
            return constant_name

    @classmethod
    def convert_unary_op(cls, unary_operator):
        """
        Depending on the concretely used operator, a string is returned.
        :param unary_operator: a single operator.
        :type unary_operator:  ASTUnaryOperator
        :return: the same operator
        :rtype: str
        """
        if unary_operator.is_unary_plus:
            return '(' + '+' + '%s' + ')'
        elif unary_operator.is_unary_minus:
            return '(' + '-' + '%s' + ')'
        elif unary_operator.is_unary_tilde:
            return '(' + '~' + '%s' + ')'
        else:
            raise RuntimeError('Cannot determine unary operator!', LoggingLevel.ERROR)

    @classmethod
    def convert_encapsulated(cls):
        """
        Converts the encapsulating parenthesis to NEST style.
        :return: a set of parenthesis
        :rtype: str
        """
        return '(%s)'

    @classmethod
    def convert_logical_not(cls):
        """
        Returns a representation of the logical not in NEST.
        :return: a string representation
        :rtype: str
        """
        return '(' + '!' + '%s' + ')'

    @classmethod
    def convert_logical_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        if op.is_logical_and:
            return '%s' + '&&' + '%s'
        elif op.is_logical_or:
            return '%s' + '||' + '%s'
        else:
            raise RuntimeError('Cannot determine logical operator!', LoggingLevel.ERROR)

    @classmethod
    def convert_comparison_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTComparisonOperator
        :return: a string representation
        :rtype: str
        """
        if op.is_lt:
            return '%s' + '<' + '%s'
        elif op.is_le:
            return '%s' + '<=' + '%s'
        elif op.is_eq:
            return '%s' + '==' + '%s'
        elif op.is_ne or op.is_ne2:
            return '%s' + '!=' + '%s'
        elif op.is_ge:
            return '%s' + '>=' + '%s'
        elif op.is_gt:
            return '%s' + '>' + '%s'
        else:
            raise RuntimeError('Cannot determine comparison operator!')

    @classmethod
    def convert_bit_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTBitOperator
        :return: a string representation
        :rtype: str
        """
        if op.is_bit_shift_left:
            return '%s' + '<<' '%s'
        if op.is_bit_shift_right:
            return '%s' + '>>' + '%s'
        if op.is_bit_and:
            return '%s' + '&' + '%s'
        if op.is_bit_or:
            return '%s' + '|' + '%s'
        if op.is_bit_xor:
            return '%s' + '^' + '%s'
        else:
            raise RuntimeError('Cannot determine bit operator!')

    @classmethod
    def convert_arithmetic_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTArithmeticOperator
        :return: a string representation
        :rtype: str
        """
        if op.is_plus_op:
            return '%s' + '+' + '%s'
        if op.is_minus_op:
            return '%s' + '-' + '%s'
        if op.is_times_op:
            return '%s' + '*' + '%s'
        if op.is_div_op:
            return '%s' + '/' + '%s'
        if op.is_modulo_op:
            return '%s' + '%' + '%s'
        if op.is_pow_op:
            return 'pow' + '(%s,%s)'
        else:
            raise RuntimeError('Cannot determine arithmetic operator!')

    @classmethod
    def convert_ternary_operator(cls):
        """
        Prints a ternary operator in NEST syntax.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'
