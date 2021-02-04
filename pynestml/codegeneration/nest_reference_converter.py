# -*- coding: utf-8 -*-
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

import re

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
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
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
    def convert_function_call(cls, function_call, prefix=''):
        """
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call : ASTFunctionCall
            The function call node to convert.
        prefix : str
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s : str
            The function call string in C++ syntax.
        """
        function_name = function_call.get_name()

        if function_name == 'and':
            return '&&'

        if function_name == 'or':
            return '||'

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            return 'nest::Time::get_resolution().get_ms()'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return 'nest::Time(nest::Time::ms((double) ({!s}))).get_steps()'

        if function_name == PredefinedFunctions.CLIP:
            # warning: the arguments of this function must swapped and
            # are therefore [v_max, v_min, v], hence its structure
            return 'std::min({2!s}, std::max({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'std::max({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'std::min({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'std::exp({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'std::log({!s})'

        if function_name == PredefinedFunctions.LOG10:
            return 'std::log10({!s})'

        if function_name == PredefinedFunctions.COSH:
            return 'std::cosh({!s})'

        if function_name == PredefinedFunctions.SINH:
            return 'std::sinh({!s})'

        if function_name == PredefinedFunctions.TANH:
            return 'std::tanh({!s})'

        if function_name == PredefinedFunctions.EXPM1:
            return 'numerics::expm1({!s})'

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return '(({!s}) + ({!s}) * ' + prefix + 'normal_dev_( nest::kernel().rng_manager.get_rng( ' + prefix + 'get_thread() ) ))'

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return '(({!s}) + ({!s}) * nest::kernel().rng_manager.get_rng( ' + prefix + 'get_thread() )->drand())'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'

        if function_name == PredefinedFunctions.PRINT:
            return 'std::cout << {!s}'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'std::cout << {!s} << std::endl'

        # suppress prefix for misc. predefined functions
        # check if function is "predefined" purely based on the name, as we don't have access to the function symbol here
        function_is_predefined = PredefinedFunctions.get_function(function_name)
        if function_is_predefined:
            prefix = ''

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return prefix + function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'
        return prefix + function_name + '()'

    def convert_name_reference(self, variable, prefix=''):
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

        assert variable.get_scope() is not None, "Undeclared variable: " + variable.get_complete_name()

        symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(variable.get_complete_name()):
                return str(UnitConverter.get_factor(PredefinedUnits.get_unit(variable.get_complete_name()).get_unit()))

            code, message = Messages.get_could_not_resolve(variable_name)
            Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                               error_position=variable.get_source_position())
            return ''

        if symbol.is_local():
            return variable_name + ('[i]' if symbol.has_vector_parameter() else '')

        if symbol.is_buffer():
            if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
                units_conversion_factor = UnitConverter.get_factor(symbol.get_type_symbol().unit.unit)
            else:
                units_conversion_factor = 1
            s = ""
            if not units_conversion_factor == 1:
                s += "(" + str(units_conversion_factor) + " * "
            s += NestPrinter.print_origin(symbol, prefix=prefix) + NestNamesConverter.buffer_value(symbol)
            if symbol.has_vector_parameter():
                s += '[i]'
            if not units_conversion_factor == 1:
                s += ")"
            return s

        if symbol.is_function:
            return 'get_' + variable_name + '()' + ('[i]' if symbol.has_vector_parameter() else '')

        if symbol.is_kernel():
            print("Printing node " + str(symbol.name))

        if symbol.is_init_values():
            temp = NestPrinter.print_origin(symbol, prefix=prefix)
            if self.uses_gsl:
                temp += GSLNamesConverter.name(symbol)
            else:
                temp += NestNamesConverter.name(symbol)
            temp += ('[i]' if symbol.has_vector_parameter() else '')
            return temp

        return NestPrinter.print_origin(symbol, prefix=prefix) + \
            NestNamesConverter.name(symbol) + \
            ('[i]' if symbol.has_vector_parameter() else '')

    def __get_unit_name(self, variable):
        assert (variable is not None and isinstance(variable, ASTVariable)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                variable)
        assert variable.get_scope() is not None, "Undeclared variable: " + variable.get_complete_name()

        variable_name = NestNamesConverter.convert_to_cpp_name(variable.get_complete_name())
        symbol = variable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
        if isinstance(symbol.get_type_symbol(), UnitTypeSymbol):
            return symbol.get_type_symbol().unit.unit.to_string()

        return ''

    def convert_print_statement(self, function_call):
        """
        A wrapper function to convert arguments of a print or println functions
        :param function_call: print function call
        :type function_call: ASTFunctionCall
        :return: the converted print string with corresponding variables, if any
        :rtype: str
        """
        stmt = function_call.get_args()[0].get_string()
        stmt = stmt[stmt.index('"') + 1: stmt.rindex('"')]  # Remove the double quotes from the string
        scope = function_call.get_scope()
        return self.__convert_print_statement_str(stmt, scope)

    def __convert_print_statement_str(self, stmt, scope):
        """
        Converts the string argument of the print or println function to NEST processable format
        Variables are resolved to NEST processable format and printed with physical units as mentioned in model, separated by a space

        .. code-block:: nestml

            print("Hello World")

        .. code-block:: C++

            std::cout << "Hello World";

        .. code-block:: nestml

            print("Membrane potential = {V_m}")

        .. code-block:: C++

            std::cout << "Membrane potential = " << V_m << " mV";

        :param stmt: argument to the print or println function
        :type stmt: str
        :param scope: scope of the variables in the argument, if any
        :type scope: Scope
        :return: the converted string to NEST
        :rtype: str
        """
        pattern = re.compile(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}')  # Match the variables enclosed within '{ }'
        match = pattern.search(stmt)
        if match:
            var_name = match.group(0)[match.group(0).find('{') + 1:match.group(0).find('}')]
            left, right = stmt.split(match.group(0), 1)  # Split on the first occurrence of a variable
            fun_left = (lambda l: self.__convert_print_statement_str(l, scope) + ' << ' if l else '')
            fun_right = (lambda r: ' << ' + self.__convert_print_statement_str(r, scope) if r else '')
            ast_var = ASTVariable(var_name, scope=scope)
            right = ' ' + self.__get_unit_name(ast_var) + right  # concatenate unit separated by a space with the right part of the string
            return fun_left(left) + self.convert_name_reference(ast_var) + fun_right(right)
        else:
            return '"' + stmt + '"'  # format bare string in C++ (add double quotes)

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
            return '%s' + ' + ' + '%s'
        if op.is_minus_op:
            return '%s' + ' - ' + '%s'
        if op.is_times_op:
            return '%s' + ' * ' + '%s'
        if op.is_div_op:
            return '%s' + ' / ' + '%s'
        if op.is_modulo_op:
            return '%s' + ' % ' + '%s'
        if op.is_pow_op:
            return 'pow' + '(%s, %s)'
        raise RuntimeError('Cannot determine arithmetic operator!')

    @classmethod
    def convert_ternary_operator(cls):
        """
        Prints a ternary operator in NEST syntax.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ') ? (' + '%s' + ') : (' + '%s' + ')'
