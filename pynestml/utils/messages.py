# -*- coding: utf-8 -*-
#
# messages.py
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
from enum import Enum
from typing import Tuple


class MessageCode(Enum):
    """
    A mapping between codes and the corresponding messages.
    """
    START_PROCESSING_FILE = 0
    TYPE_REGISTERED = 1
    START_SYMBOL_TABLE_BUILDING = 2
    FUNCTION_CALL_TYPE_ERROR = 3
    TYPE_NOT_DERIVABLE = 4
    IMPLICIT_CAST = 5
    CAST_NOT_POSSIBLE = 6
    TYPE_DIFFERENT_FROM_EXPECTED = 7
    ADD_SUB_TYPE_MISMATCH = 8
    BUFFER_SET_TO_CONDUCTANCE_BASED = 9
    ODE_UPDATED = 10
    NO_VARIABLE_FOUND = 11
    SPIKE_BUFFER_TYPE_NOT_DEFINED = 12
    NEURON_CONTAINS_ERRORS = 13
    START_PROCESSING_NEURON = 14
    CODE_SUCCESSFULLY_GENERATED = 15
    MODULE_SUCCESSFULLY_GENERATED = 16
    NO_CODE_GENERATED = 17
    VARIABLE_USED_BEFORE_DECLARATION = 18
    VARIABLE_DEFINED_RECURSIVELY = 19
    VALUE_ASSIGNED_TO_BUFFER = 20
    ARG_NOT_KERNEL_OR_EQUATION = 21
    ARG_NOT_BUFFER = 22
    NUMERATOR_NOT_ONE = 23
    ORDER_NOT_DECLARED = 24
    CURRENT_BUFFER_SPECIFIED = 25
    BLOCK_NOT_CORRECT = 26
    VARIABLE_NOT_IN_INIT = 27
    WRONG_NUMBER_OF_ARGS = 28
    NO_RHS = 29
    SEVERAL_LHS = 30
    FUNCTION_REDECLARED = 31
    FUNCTION_NOT_DECLARED = 52
    NO_ODE = 32
    NO_INIT_VALUE = 33
    NEURON_REDECLARED = 34
    NEST_COLLISION = 35
    KERNEL_OUTSIDE_CONVOLVE = 36
    NAME_COLLISION = 37
    TYPE_NOT_SPECIFIED = 38
    NO_TYPE_ALLOWED = 39
    NO_ASSIGNMENT_ALLOWED = 40
    NOT_A_VARIABLE = 41
    MULTIPLE_KEYWORDS = 42
    VECTOR_IN_NON_VECTOR = 43
    VARIABLE_REDECLARED = 44
    SOFT_INCOMPATIBILITY = 45
    HARD_INCOMPATIBILITY = 46
    NO_RETURN = 47
    NOT_LAST_STATEMENT = 48
    SYMBOL_NOT_RESOLVED = 49
    TYPE_MISMATCH = 50
    NO_SEMANTICS = 51
    NEURON_SOLVED_BY_GSL = 52
    NEURON_ANALYZED = 53
    NO_UNIT = 54
    NOT_NEUROSCIENCE_UNIT = 55
    INTERNAL_WARNING = 56
    OPERATION_NOT_DEFINED = 57
    CONVOLVE_NEEDS_BUFFER_PARAMETER = 58
    INPUT_PATH_NOT_FOUND = 59
    LEXER_ERROR = 60
    PARSER_ERROR = 61
    UNKNOWN_TARGET = 62
    VARIABLE_WITH_SAME_NAME_AS_UNIT = 63
    ANALYSING_TRANSFORMING_NEURON = 64
    ODE_NEEDS_CONSISTENT_UNITS = 65
    TEMPLATED_ARG_TYPES_INCONSISTENT = 66
    MODULE_NAME_INFO = 67
    TARGET_PATH_INFO = 68
    ODE_FUNCTION_NEEDS_CONSISTENT_UNITS = 69
    DELTA_FUNCTION_CANNOT_BE_MIXED = 70
    UNKNOWN_TYPE = 71
    ASTDATATYPE_TYPE_SYMBOL_COULD_NOT_BE_DERIVED = 72
    KERNEL_WRONG_TYPE = 73
    KERNEL_IV_WRONG_TYPE = 74
    EMIT_SPIKE_FUNCTION_BUT_NO_OUTPUT_PORT = 75
    NO_FILES_IN_INPUT_PATH = 76


class Messages(object):
    """
    This class contains a collection of error messages which enables a centralized maintaining and modifications of
    those.
    """

    @classmethod
    def get_start_processing_file(cls, file_path):
        """
        Returns a message indicating that processing of a file has started
        :param file_path: the path to the file
        :type file_path: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'Start processing \'' + file_path + '\'!'
        return MessageCode.START_PROCESSING_FILE, message

    @classmethod
    def get_new_type_registered(cls, type_name):
        """
        Returns a message which indicates that a new type has been registered.
        :param type_name: a type name
        :type type_name: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'New type registered \'%s\'!' % type_name
        return MessageCode.TYPE_REGISTERED, message

    @classmethod
    def get_input_path_not_found(cls, path):
        message = 'Input path ("%s") not found!' % (path)
        return MessageCode.INPUT_PATH_NOT_FOUND, message

    @classmethod
    def get_unknown_target(cls, target):
        message = 'Unknown target ("%s")' % (target)
        return MessageCode.UNKNOWN_TARGET, message

    @classmethod
    def get_no_code_generated(cls):
        """
        Returns a message indicating that no code will be generated on this run.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'No target specified: no code will be generated'
        return MessageCode.NO_CODE_GENERATED, message

    @classmethod
    def get_lexer_error(cls):
        message = 'Error occurred during lexing: abort'
        return MessageCode.LEXER_ERROR, message

    @classmethod
    def get_parser_error(cls):
        message = 'Error occurred during parsing: abort'
        return MessageCode.PARSER_ERROR, message

    @classmethod
    def get_binary_operation_not_defined(cls, lhs, operator, rhs):
        message = 'Operation %s %s %s is not defined!' % (lhs, operator, rhs)
        return MessageCode.OPERATION_NOT_DEFINED, message

    @classmethod
    def get_binary_operation_type_could_not_be_derived(cls, lhs, operator, rhs, lhs_type, rhs_type):
        message = 'The type of the expression (left-hand side = \'%s\'; binary operator = \'%s\'; right-hand side = \'%s\') could not be derived: left-hand side has type \'%s\' whereas right-hand side has type \'%s\'!' % (
            lhs, operator, rhs, lhs_type, rhs_type)
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_unary_operation_not_defined(cls, operator, term):
        message = 'Operation %s%s is not defined!' % (operator, term)
        return MessageCode.OPERATION_NOT_DEFINED, message

    @classmethod
    def get_convolve_needs_buffer_parameter(cls):
        message = 'Convolve requires a buffer variable as second parameter!'
        return MessageCode.CONVOLVE_NEEDS_BUFFER_PARAMETER, message

    @classmethod
    def get_implicit_magnitude_conversion(cls, lhs, rhs, conversion_factor):
        message = 'Non-matching unit types at %s +/- %s! ' \
                  'Implicitly replaced by %s +/- %s * %s.' % (
                      lhs.print_symbol(), rhs.print_symbol(), lhs.print_symbol(), conversion_factor,
                      rhs.print_symbol())
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def get_start_building_symbol_table(cls):
        """
        Returns a message that the building for a neuron has been started.
        :return: a message
        :rtype: (MessageCode,str)
        """
        return MessageCode.START_SYMBOL_TABLE_BUILDING, 'Start building symbol table!'

    @classmethod
    def get_function_call_implicit_cast(cls, arg_nr, function_call, expected_type, got_type, castable=False):
        """
        Returns a message indicating that an implicit cast has been performed.
        :param arg_nr: the number of the argument which is cast
        :type arg_nr: int
        :param function_call: a single function call
        :type function_call: ast_function_call
        :param expected_type: the expected type
        :type expected_type: type_symbol
        :param got_type: the got-type
        :type got_type: TypeSymbol
        :param castable: is the type castable
        :type castable: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        if not castable:
            message = str(arg_nr) + '. argument of function-call \'%s\' at is wrongly typed! Expected \'%s\',' \
                                    ' found \'%s\'!' % (function_call.get_name(), got_type.print_symbol(),
                                                        expected_type.print_symbol())
        else:
            message = str(arg_nr) + '. argument of function-call \'%s\' is wrongly typed! ' \
                                    'Implicit cast from \'%s\' to \'%s\'.' % (function_call.get_name(),
                                                                              got_type.print_symbol(),
                                                                              expected_type.print_symbol())
        return MessageCode.FUNCTION_CALL_TYPE_ERROR, message

    @classmethod
    def get_type_could_not_be_derived(cls, rhs):
        """
        Returns a message indicating that the type of the rhs rhs could not be derived.
        :param rhs: an rhs
        :type rhs: ast_expression or ast_simple_expression
        :return: a message
        :rtype: (MessageCode,str)

        """
        message = 'Type of \'%s\' could not be derived!' % rhs
        return MessageCode.TYPE_NOT_DERIVABLE, message

    @classmethod
    def get_implicit_cast_rhs_to_lhs(cls, rhs_type, lhs_type):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs, but the rhs
        can be cast down to lhs type.
        :param rhs_type: the type of the rhs
        :type rhs_type: str
        :param lhs_type: the type of the lhs
        :type lhs_type: str
        :return: a message
        :rtype:(MessageCode,str)
        """
        message = 'Implicit casting from (compatible) type \'%s\' to \'%s\'.' % (rhs_type, lhs_type)
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def get_different_type_rhs_lhs(cls, rhs_expression, lhs_expression, rhs_type, lhs_type):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs and can not
        be cast down to a common type.
        :param rhs_expression: the rhs rhs
        :type rhs_expression: ASTExpression or ASTSimpleExpression
        :param lhs_expression: the lhs rhs
        :type lhs_expression: ast_expression or ast_simple_expression
        :param rhs_type: the type of the rhs
        :type rhs_type: type_symbol
        :param lhs_type: the type of the lhs
        :type lhs_type: TypeSymbol
        :return: a message
        :rtype:(MessageCode,str)
        """
        message = 'Type of lhs \'%s\' does not correspond to rhs \'%s\'! LHS: \'%s\', RHS: \'%s\'!' % (
            lhs_expression,
            rhs_expression,
            lhs_type.print_symbol(),
            rhs_type.print_symbol())
        return MessageCode.CAST_NOT_POSSIBLE, message

    @classmethod
    def get_type_different_from_expected(cls, expected_type, got_type):
        """
        Returns a message indicating that the received type is different from the expected one.
        :param expected_type: the expected type
        :type expected_type: TypeSymbol
        :param got_type: the actual type
        :type got_type: type_symbol
        :return: a message
        :rtype: (MessageCode,str)
        """
        from pynestml.symbols.type_symbol import TypeSymbol
        assert (expected_type is not None and isinstance(expected_type, TypeSymbol)), \
            '(PyNestML.Utils.Message) Not a type symbol provided (%s)!' % type(expected_type)
        assert (got_type is not None and isinstance(got_type, TypeSymbol)), \
            '(PyNestML.Utils.Message) Not a type symbol provided (%s)!' % type(got_type)
        message = 'Actual type different from expected. Expected: \'%s\', got: \'%s\'!' % (
            expected_type.print_symbol(), got_type.print_symbol())
        return MessageCode.TYPE_DIFFERENT_FROM_EXPECTED, message

    @classmethod
    def get_buffer_set_to_conductance_based(cls, buffer):
        """
        Returns a message indicating that a buffer has been set to conductance based.
        :param buffer: the name of the buffer
        :type buffer: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (buffer is not None and isinstance(buffer, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(buffer)
        message = 'Buffer \'%s\' set to conductance based!' % buffer
        return MessageCode.BUFFER_SET_TO_CONDUCTANCE_BASED, message

    @classmethod
    def get_ode_updated(cls, variable_name):
        """
        Returns a message indicating that the ode of a variable has been updated.
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Ode of \'%s\' updated!' % variable_name
        return MessageCode.ODE_UPDATED, message

    @classmethod
    def get_no_variable_found(cls, variable_name):
        """
        Returns a message indicating that a variable has not been found.
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'No variable \'%s\' found!' % variable_name
        return MessageCode.NO_VARIABLE_FOUND, message

    @classmethod
    def get_buffer_type_not_defined(cls, buffer_name):
        """
        Returns a message indicating that a buffer type has not been defined, thus nS is assumed.
        :param buffer_name: a buffer name
        :type buffer_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (buffer_name is not None and isinstance(buffer_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(buffer_name)
        from pynestml.symbols.predefined_types import PredefinedTypes
        message = 'No buffer type declared of \'%s\'!' % buffer_name
        return MessageCode.SPIKE_BUFFER_TYPE_NOT_DEFINED, message

    @classmethod
    def get_neuron_contains_errors(cls, neuron_name):
        """
        Returns a message indicating that a neuron contains errors thus no code is generated.
        :param neuron_name: the name of the neuron
        :type neuron_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        message = 'Neuron \'' + neuron_name + '\' contains errors. No code generated!'
        return MessageCode.NEURON_CONTAINS_ERRORS, message

    @classmethod
    def get_start_processing_neuron(cls, neuron_name):
        """
        Returns a message indicating that the processing of a neuron is started.
        :param neuron_name: the name of the neuron
        :type neuron_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        message = 'Starts processing of the neuron \'' + neuron_name + '\''
        return MessageCode.START_PROCESSING_NEURON, message

    @classmethod
    def get_code_generated(cls, neuron_name, path):
        """
        Returns a message indicating that code has been successfully generated for a neuron in a certain path.
        :param neuron_name: the name of the neuron.
        :type neuron_name: str
        :param path: the path to the file
        :type path: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        assert (path is not None and isinstance(path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(path)
        message = 'Successfully generated code for the neuron: \'' + neuron_name + '\' in: \'' + path + '\' !'
        return MessageCode.CODE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def get_module_generated(cls, path):
        """
        Returns a message indicating that a module has been successfully generated.
        :param path: the path to the generated file
        :type path: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (path is not None and isinstance(path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(path)
        message = 'Successfully generated NEST module code in \'' + path + '\' !'
        return MessageCode.MODULE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def get_variable_used_before_declaration(cls, variable_name):
        """
        Returns a message indicating that a variable is used before declaration.
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' used before declaration!' % variable_name
        return MessageCode.VARIABLE_USED_BEFORE_DECLARATION, message

    @classmethod
    def get_variable_not_defined(cls, variable_name):
        """
        Returns a message indicating that a variable is not defined .
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' not defined!' % variable_name
        return MessageCode.NO_VARIABLE_FOUND, message

    @classmethod
    def get_variable_defined_recursively(cls, variable_name):
        """
        Returns a message indicating that a variable is defined recursively.
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' defined recursively!' % variable_name
        return MessageCode.VARIABLE_DEFINED_RECURSIVELY, message

    @classmethod
    def get_value_assigned_to_buffer(cls, buffer_name):
        """
        Returns a message indicating that a value has been assigned to a buffer.
        :param buffer_name: a buffer name
        :type buffer_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (buffer_name is not None and isinstance(buffer_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(buffer_name)
        message = 'Value assigned to buffer \'%s\'!' % buffer_name
        return MessageCode.VALUE_ASSIGNED_TO_BUFFER, message

    @classmethod
    def get_first_arg_not_kernel_or_equation(cls, func_name):
        """
        Indicates that the first argument of an rhs is not an equation or kernel.
        :param func_name: the name of the function
        :type func_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (func_name is not None and isinstance(func_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(func_name)
        message = 'First argument of \'%s\' not a kernel or equation!' % func_name
        return MessageCode.ARG_NOT_KERNEL_OR_EQUATION, message

    @classmethod
    def get_second_arg_not_a_buffer(cls, func_name):
        """
        Indicates that the second argument of an rhs is not a buffer.
        :param func_name: the name of the function
        :type func_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (func_name is not None and isinstance(func_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(func_name)
        message = 'Second argument of \'%s\' not a buffer!' % func_name
        return MessageCode.ARG_NOT_BUFFER, message

    @classmethod
    def get_wrong_numerator(cls, unit):
        """
        Indicates that the numerator of a unit is not 1.
        :param unit: the name of the unit
        :type unit: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (unit is not None and isinstance(unit, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(unit)
        message = 'Numeric numerator of unit \'%s\' not 1!' % unit
        return MessageCode.NUMERATOR_NOT_ONE, message

    @classmethod
    def get_order_not_declared(cls, lhs):
        """
        Indicates that the order has not been declared.
        :param lhs: the name of the variable
        :type lhs: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (lhs is not None and isinstance(lhs, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % lhs
        message = 'Order of differential equation for %s is not declared!' % lhs
        return MessageCode.ORDER_NOT_DECLARED, message

    @classmethod
    def get_current_buffer_specified(cls, name, keyword):
        """
        Indicates that the current buffer has been specified with a type keyword.
        :param name: the name of the buffer
        :type name: str
        :param keyword: the keyword
        :type keyword: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % name
        message = 'Current buffer \'%s\' specified with type keywords (%s)!' % (name, keyword)
        return MessageCode.CURRENT_BUFFER_SPECIFIED, message

    @classmethod
    def get_block_not_defined_correctly(cls, block, missing):
        """
        Indicates that a given block has been defined several times or non.
        :param block: the name of the block which is not defined or defined multiple times.
        :type block: str
        :param missing: True if missing, False if multiple times.
        :type missing: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (block is not None and isinstance(block, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(block)
        assert (missing is not None and isinstance(missing, bool)), \
            '(PyNestML.Utils.Message) Not a bool provided (%s)!' % type(missing)
        if missing:
            message = block + ' block not defined!'
        else:
            message = block + ' block defined more than once!'
        return MessageCode.BLOCK_NOT_CORRECT, message

    @classmethod
    def get_equation_var_not_in_init_values_block(cls, variable_name):
        """
        Indicates that a variable in the equations block is not defined in the initial values block.
        :param variable_name: the name of the variable of an equation which is not defined in an equations block
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Ode equation lhs-variable \'%s\' not defined in initial-values block!' % variable_name
        return MessageCode.VARIABLE_NOT_IN_INIT, message

    @classmethod
    def get_wrong_number_of_args(cls, function_call, expected, got):
        """
        Indicates that a wrong number of arguments has been provided to the function call.
        :param function_call: a function call name
        :type function_call: str
        :param expected: the expected number of arguments
        :type expected: int
        :param got: the given number of arguments
        :type got: int
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (function_call is not None and isinstance(function_call, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(function_call)
        assert (expected is not None and isinstance(expected, int)), \
            '(PyNestML.Utils.Message) Not a int provided (%s)!' % type(expected)
        assert (got is not None and isinstance(got, int)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(got)
        message = 'Wrong number of arguments in function-call \'%s\'! Expected \'%s\', found \'%s\'.' % (
            function_call, expected, got)
        return MessageCode.WRONG_NUMBER_OF_ARGS, message

    @classmethod
    def get_no_rhs(cls, name):
        """
        Indicates that no right-hand side has been declared for the given variable.
        :param name: the name of the rhs variable
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function variable \'%s\' has no right-hand side!' % name
        return MessageCode.NO_RHS, message

    @classmethod
    def get_several_lhs(cls, names):
        """
        Indicates that several left hand sides have been defined.
        :param names: a list of variables
        :type names: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (names is not None and isinstance(names, list)), \
            '(PyNestML.Utils.Message) Not a list provided (%s)!' % type(names)
        message = 'Function declared with several variables (%s)!' % names
        return MessageCode.SEVERAL_LHS, message

    @classmethod
    def get_function_redeclared(cls, name, predefined):
        """
        Indicates that a function has been redeclared.
        :param name: the name of the function which has been redeclared.
        :type name: str
        :param predefined: True if function is predefined, otherwise False.
        :type predefined: bool
        :return: a message
        :rtype:(MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        if predefined:
            message = 'Predefined function \'%s\' redeclared!' % name
        else:
            message = 'Function \'%s\' redeclared!' % name
        return MessageCode.FUNCTION_REDECLARED, message

    @classmethod
    def get_no_ode(cls, name):
        """
        Indicates that no ODE has been defined for a variable inside the initial values block.
        :param name: the name of the variable which does not have a defined ode
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Variable \'%s\' not provided with an ODE!' % name
        return MessageCode.NO_ODE, message

    @classmethod
    def get_no_init_value(cls, name):
        """
        Indicates that no initial value has been provided for a given variable.
        :param name: the name of the variable which does not have a initial value
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Initial value of ode variable \'%s\' not provided!' % name
        return MessageCode.NO_INIT_VALUE, message

    @classmethod
    def get_neuron_redeclared(cls, name):
        """
        Indicates that a neuron has been redeclared.
        :param name: the name of the neuron which has been redeclared.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Neuron \'%s\' redeclared!' % name
        return MessageCode.NEURON_REDECLARED, message

    @classmethod
    def get_nest_collision(cls, name):
        """
        Indicates that a collision between a user defined function and a nest function occurred.
        :param name: the name of the function which collides to nest
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function \'%s\' collides with NEST namespace!' % name
        return MessageCode.NEST_COLLISION, message

    @classmethod
    def get_kernel_outside_convolve(cls, name):
        """
        Indicates that a kernel variable has been used outside a convolve call.
        :param name: the name of the kernel
        :type name: str
        :return: message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Kernel \'%s\' used outside convolve!' % name
        return MessageCode.KERNEL_OUTSIDE_CONVOLVE, message

    @classmethod
    def get_compilation_unit_name_collision(cls, name, art1, art2):
        """
        Indicates that a name collision with the same neuron inside two artifacts.
        :param name: the name of the neuron which leads to collision
        :type name: str
        :param art1: the first artifact name
        :type art1: str
        :param art2: the second artifact name
        :type art2: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (art1 is not None and isinstance(art1, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(art1)
        assert (art2 is not None and isinstance(art2, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(art2)
        message = 'Name collision of \'%s\' in \'%s\' and \'%s\'!' % (name, art1, art2)
        return MessageCode.NAME_COLLISION, message

    @classmethod
    def get_data_type_not_specified(cls, name):
        """
        Indicates that for a given element no type has been specified.
        :param name: the name of the variable for which a type has not been specified.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Data type of \'%s\' at not specified!' % name
        return MessageCode.TYPE_NOT_SPECIFIED, message

    @classmethod
    def get_not_type_allowed(cls, name):
        """
        Indicates that a type for the given element is not allowed.
        :param name: the name of the element for which a type is not allowed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'No data type allowed for \'%s\'!' % name
        return MessageCode.NO_TYPE_ALLOWED, message

    @classmethod
    def get_assignment_not_allowed(cls, name):
        """
        Indicates that an assignment to the given element is not allowed.
        :param name: the name of variable to which an assignment is not allowed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Assignment to \'%s\' not allowed!' % name
        return MessageCode.NO_ASSIGNMENT_ALLOWED, message

    @classmethod
    def get_not_a_variable(cls, name):
        """
        Indicates that a given name does not represent a variable.
        :param name: the name of the variable
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = '\'%s\' not a variable!' % name
        return MessageCode.NOT_A_VARIABLE, message

    @classmethod
    def get_multiple_keywords(cls, keyword):
        """
        Indicates that a buffer has been declared with multiple keywords of the same type, e.g., inhibitory inhibitory
        :param keyword: the keyword which has been used multiple times
        :type keyword: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (keyword is not None and isinstance(keyword, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(keyword)
        message = 'Buffer specified with multiple \'%s\' keywords!' % keyword
        return MessageCode.MULTIPLE_KEYWORDS, message

    @classmethod
    def get_vector_in_non_vector(cls, vector, non_vector):
        """
        Indicates that a vector has been used in a non-vector declaration.
        :param vector: the vector variable
        :type vector: str
        :param non_vector: the non-vector lhs
        :type non_vector: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (vector is not None and isinstance(vector, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(vector)
        assert (non_vector is not None and isinstance(non_vector, list)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(non_vector)
        message = 'Vector value \'%s\' used in a non-vector declaration of variables \'%s\'!' % (vector, non_vector)
        return MessageCode.VECTOR_IN_NON_VECTOR, message

    @classmethod
    def get_variable_redeclared(cls, name, predefined):
        """
        Indicates that a given variable has been redeclared. A redeclaration can happen with user defined
        functions or with predefined functions (second parameter).
        :param name: the name of the variable
        :type name: str
        :param predefined: True if a pre-defined variable has been redeclared, otherwise False.
        :type predefined: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (predefined is not None and isinstance(predefined, bool)), \
            '(PyNestML.Utils.Message) Not a bool provided (%s)!' % type(predefined)
        if predefined:
            message = 'Predefined variable \'%s\' redeclared!' % name
        else:
            message = 'Variable \'%s\' redeclared !' % name
        return MessageCode.VARIABLE_REDECLARED, message

    @classmethod
    def get_no_return(cls):
        """
        Indicates that a given function has no return statement although required.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Return statement expected!'
        return MessageCode.NO_RETURN, message

    @classmethod
    def get_not_last_statement(cls, name):
        """
        Indicates that given statement is not the last statement in a block, e.g., in the case that a return
        statement is not the last statement.
        :param name: the statement.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = '\'%s\' not the last statement!' % name
        return MessageCode.NOT_LAST_STATEMENT, message

    @classmethod
    def get_function_not_declared(cls, name):
        """
        Indicates that a function, which is not declared, has been used.
        :param name: the name of the function.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function \'%s\' is not declared!' % name
        return MessageCode.FUNCTION_NOT_DECLARED, message

    @classmethod
    def get_could_not_resolve(cls, name):
        """
        Indicates that the handed over name could not be resolved to a symbol.
        :param name: the name which could not be resolved
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Could not resolve symbol \'%s\'!' % name
        return MessageCode.SYMBOL_NOT_RESOLVED, message

    @classmethod
    def get_neuron_solved_by_solver(cls, name):
        """
        Indicates that a neuron will be solved by the GSL solver inside the model printing process without any
        modifications to the initial model.
        :param name: the name of the neuron
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'The neuron \'%s\' will be solved numerically with GSL solver without modification!' % name
        return MessageCode.NEURON_SOLVED_BY_GSL, message

    @classmethod
    def get_neuron_analyzed(cls, name):
        """
        Indicates that the analysis of a neuron will start.
        :param name: the name of the neuron which will be analyzed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'The neuron \'%s\' will be analysed!' % name
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_could_not_be_solved(cls):
        """
        Indicates that the set of equations could not be solved and will remain unchanged.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Equations or kernels could not be solved. The model remains unchanged!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_equations_solved_exactly(cls):
        """
        Indicates that all equations of the neuron are solved exactly by the solver script.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Equations are solved exactly!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_equations_solved_by_gls(cls):
        """
        Indicates that the set of ODEs as contained in the model will be solved by the gnu scientific library toolchain.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Kernels will be solved with GLS!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_ode_solution_not_used(cls):
        """
        Indicates that an ode has been defined in the model but is not used as part of the neurons solution.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'The model has defined an ODE. But its solution is not used in the update state.'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_unit_does_not_exist(cls, name):
        """
        Indicates that a unit does not exist.
        :param name: the name of the unit.
        :type name: str
        :return: a new code,message tuple
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Unit does not exist (%s).' % name
        return MessageCode.NO_UNIT, message

    @classmethod
    def get_not_neuroscience_unit_used(cls, name):
        """
        Indicates that a non-neuroscientific unit, e.g., kg, has been used. Those units can not be converted to
        a corresponding representation in the simulation and are therefore represented by the factor 1.
        :param name: the name of the variable
        :type name: str
        :return: a nes code,message tuple
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Not convertible unit \'%s\' used, 1 assumed as factor!' % name
        return MessageCode.NOT_NEUROSCIENCE_UNIT, message

    @classmethod
    def get_ode_needs_consistent_units(cls, name, differential_order, lhs_type, rhs_type):
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'ODE definition for \''
        if differential_order > 1:
            message += 'd^' + str(differential_order) + ' ' + name + ' / dt^' + str(differential_order) + '\''
        if differential_order > 0:
            message += 'd ' + name + ' / dt\''
        else:
            message += '\'' + str(name) + '\''
        message += ' has inconsistent units: expected \'' + lhs_type.print_symbol() + '\', got \'' + \
            rhs_type.print_symbol() + '\''
        return MessageCode.ODE_NEEDS_CONSISTENT_UNITS, message

    @classmethod
    def get_ode_function_needs_consistent_units(cls, name, declared_type, expression_type):
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'ODE function definition for \'' + name + '\' has inconsistent units: expected \'' + \
            declared_type.print_symbol() + '\', got \'' + expression_type.print_symbol() + '\''
        return MessageCode.ODE_FUNCTION_NEEDS_CONSISTENT_UNITS, message

    @classmethod
    def get_variable_with_same_name_as_type(cls, name):
        """
        Indicates that a variable has been declared with the same name as a physical unit, e.g. "V mV"
        :param name: the name of the variable
        :type name: str
        :return: a tuple containing message code and message text
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Variable \'%s\' has the same name as a physical unit!' % name
        return MessageCode.VARIABLE_WITH_SAME_NAME_AS_UNIT, message

    @classmethod
    def get_analysing_transforming_neuron(cls, name):
        """
        Indicates start of code generation
        :param name: the name of the neuron model
        :type name: ASTNeuron
        :return: a nes code,message tuple
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Analysing/transforming neuron \'%s\'' % name
        return MessageCode.ANALYSING_TRANSFORMING_NEURON, message

    @classmethod
    def templated_arg_types_inconsistent(cls, function_name, failing_arg_idx, other_args_idx, failing_arg_type_str, other_type_str):
        """
        For templated function arguments, indicates inconsistency between (formal) template argument types and actual derived types.
        :param name: the name of the neuron model
        :type name: ASTNeuron
        :return: a nes code,message tuple
        :rtype: (MessageCode,str)
        """
        message = 'In function \'' + function_name + '\': actual derived type of templated parameter ' + \
            str(failing_arg_idx + 1) + ' is \'' + failing_arg_type_str + '\', which is inconsistent with that of parameter(s) ' + \
            ', '.join([str(_ + 1) for _ in other_args_idx]) + ', which have type \'' + other_type_str + '\''
        return MessageCode.TEMPLATED_ARG_TYPES_INCONSISTENT, message

    @classmethod
    def delta_function_cannot_be_mixed(cls):
        """
        Delta function cannot be mixed with expressions.
        """
        message = "delta function cannot be mixed with expressions; please instead perform these operations on the convolve() function where this kernel is used"
        return MessageCode.DELTA_FUNCTION_CANNOT_BE_MIXED, message

    @classmethod
    def delta_function_one_arg(cls, deltafunc):
        """
        Delta function takes exactly one argument.
        :param deltafunc: the delta function node
        :type name: ASTFunctionCall
        """
        message = "delta function takes exactly one argument (time *t*); instead found " + ", ".join([
            str(arg) for arg in deltafunc.get_args()])
        return MessageCode.DELTA_FUNCTION_CANNOT_BE_MIXED, message

    @classmethod
    def unknown_type(cls, provided_type_str):
        """
        Unknown type or unit literal.
        :param provided_type_str: the provided type as a string
        :type provided_type_str: str
        """
        message = "Unknown type or unit literal: " + provided_type_str
        return MessageCode.UNKNOWN_TYPE, message

    @classmethod
    def astdatatype_type_symbol_could_not_be_derived(cls):
        """
        Unknown type or unit literal.
        :param provided_type_str: the provided type as a string
        :type provided_type_str: str
        """
        message = "ASTDataType type symbol could not be derived"
        return MessageCode.ASTDATATYPE_TYPE_SYMBOL_COULD_NOT_BE_DERIVED, message

    @classmethod
    def get_emit_spike_function_but_no_output_port(cls):
        """
        Indicates that an emit_spike() function was called, but no spiking output port has been defined.
        :return: a (code, message) tuple
        :rtype: (MessageCode, str)
        """
        message = 'emit_spike() function was called, but no spiking output port has been defined!'
        return MessageCode.EMIT_SPIKE_FUNCTION_BUT_NO_OUTPUT_PORT, message

    @classmethod
    def get_kernel_wrong_type(cls, kernel_name: str, differential_order: int, actual_type: str) -> Tuple[MessageCode, str]:
        """
        Returns a message indicating that the type of a kernel is wrong.
        :param kernel_name: the name of the kernel
        :param differential_order: differential order of the kernel left-hand side, e.g. 2 if the kernel is g''
        :param actual_type: the name of the actual type that was found in the model
        """
        assert (kernel_name is not None and isinstance(kernel_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(kernel_name)
        if differential_order == 0:
            expected_type_str = "real or int"
        else:
            assert differential_order > 0
            expected_type_str = "s**-%d" % differential_order
        message = 'Kernel \'%s\' was found to be of type \'%s\' (should be %s)!' % (
            kernel_name, actual_type, expected_type_str)
        return MessageCode.KERNEL_WRONG_TYPE, message

    @classmethod
    def get_kernel_iv_wrong_type(cls, iv_name: str, actual_type: str, expected_type: str) -> Tuple[MessageCode, str]:
        """
        Returns a message indicating that the type of a kernel initial value is wrong.
        :param iv_name: the name of the initial value variable
        :param actual_type: the name of the actual type that was found in the model
        :param expected_type: the name of the type that was expected
        """
        message = 'Initial value \'%s\' was found to be of type \'%s\' (should be %s)!' % (iv_name, actual_type, expected_type)
        return MessageCode.KERNEL_IV_WRONG_TYPE, message

    @classmethod
    def get_could_not_determine_cond_based(cls, type_str, name):
        message = "Unable to determine based on type '" + type_str + \
            "' of variable '" + name + "' whether conductance-based or current-based"
        return MessageCode.LEXER_ERROR, message

    @classmethod
    def get_no_files_in_input_path(cls, path: str):
        message = "No files found matching '*.nestml' in provided input path '" + path + "'"
        return MessageCode.NO_FILES_IN_INPUT_PATH, message
