# -*- coding: utf-8 -*-
#
# variable_symbol.py
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
from copy import copy

from enum import Enum

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import Symbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages

from astropy import units


class VariableSymbol(Symbol):
    """
    This class is used to store a single variable symbol containing all required information.

    Attributes:
        block_type           The type of block in which this symbol has been declared. Type: BlockType
        vector_parameter     The parameter indicating the position in an array. Type: str
        declaring_expression The rhs defining the value of this symbol. Type: ASTExpression
        is_predefined        Indicates whether this symbol is predefined, e.g., t or e. Type: bool
        is_function          Indicates whether this symbol belongs to a function. Type: bool
        is_recordable        Indicates whether this symbol belongs to a recordable element. Type: bool
        type_symbol          The concrete type of this variable.
        ode_declaration      Used to store the corresponding ode declaration.
        is_conductance_based  Indicates whether this buffer is conductance based.
        initial_value        Indicates the initial value if such is declared.
        variable_type        The type of the variable, either a kernel, or buffer or function. Type: VariableType
    """

    def __init__(self, element_reference=None, scope=None, name=None, block_type=None, vector_parameter=None,
                 declaring_expression=None, is_predefined=False, is_function=False, is_recordable=False,
                 type_symbol=None, initial_value=None, variable_type=None):
        """
        Standard constructor.
        :param element_reference: a reference to the first element where this type has been used/defined
        :type element_reference: Object (or None, if predefined)
        :param scope: the scope in which this type is defined in
        :type scope: Scope
        :param name: the name of the type symbol
        :type name: str
        :param block_type: the type of block in which this element has been defined in
        :type block_type: BlockType
        :param vector_parameter: the parameter indicating a position in an array
        :type vector_parameter: str
        :param declaring_expression: a rhs declaring the value of this symbol.
        :type declaring_expression: ASTExpression
        :param is_predefined: indicates whether this element represents a predefined variable, e.g., e or t
        :type is_predefined: bool
        :param is_function: indicates whether this element represents a function (aka. alias)
        :type is_function: bool
        :param is_recordable: indicates whether this elements is recordable or not.
        :type is_recordable: bool
        :param type_symbol: a type symbol representing the concrete type of this variable
        :type type_symbol: type_symbol
        :param initial_value: the initial value if such an exists
        :type initial_value: ASTExpression
        :param variable_type: the type of the variable
        :type variable_type: VariableType
        """
        super(VariableSymbol, self).__init__(element_reference=element_reference, scope=scope,
                                             name=name, symbol_kind=SymbolKind.VARIABLE)
        self.block_type = block_type
        self.vector_parameter = vector_parameter
        self.declaring_expression = declaring_expression
        self.is_predefined = is_predefined
        self.is_function = is_function
        self.is_recordable = is_recordable
        self.type_symbol = type_symbol
        self.initial_value = initial_value
        self.variable_type = variable_type
        self.ode_or_kernel = None

    def has_vector_parameter(self):
        """
        Returns whether this variable symbol has a vector parameter.
        :return: True if vector parameter available, otherwise False.
        :rtype: bool
        """
        return self.vector_parameter is not None and type(self.vector_parameter) == str

    def get_block_type(self):
        """
        Returns the block type
        :return: the block type
        :rtype: BlockType
        """
        return self.block_type

    def get_vector_parameter(self):
        """
        Returns the vector parameter of this symbol if any available, e.g., spike[12]
        :return: the vector parameter of this variable symbol.
        :rtype: str
        """
        return self.vector_parameter

    def get_declaring_expression(self):
        """
        Returns the rhs declaring the value of this symbol.
        :return: the rhs declaring the value.
        :rtype: ASTExpression
        """
        return self.declaring_expression

    def has_declaring_expression(self) -> bool:
        """
        Indicates whether a declaring rhs is present.
        :return: True if present, otherwise False.
        :rtype: bool
        """
        return self.declaring_expression is not None and (isinstance(self.declaring_expression, ASTSimpleExpression)
                                                          or isinstance(self.declaring_expression, ASTExpression))

    def is_spike_buffer(self) -> bool:
        """
        Returns whether this symbol represents a spike buffer.
        :return: True if spike buffer, otherwise False.
        :rtype: bool
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_spike()

    def is_current_buffer(self) -> bool:
        """
        Returns whether this symbol represents a current buffer.
        :return: True if current buffer, otherwise False.
        :rtype: bool
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_current()

    def is_excitatory(self) -> bool:
        """
        Returns whether this symbol represents a buffer of type excitatory.
        :return: True if is excitatory, otherwise False.
        :rtype: bool
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_excitatory()

    def is_inhibitory(self) -> bool:
        """
        Returns whether this symbol represents a buffer of type inhibitory.
        :return: True if is inhibitory, otherwise False.
        :rtype: bool
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_inhibitory()

    def is_state(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a state block.
        :return: True if declared in a state block, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.STATE

    def is_parameters(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a parameters block.
        :return: True if declared in a parameters block, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.PARAMETERS

    def is_internals(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a internals block.
        :return: True if declared in a internals block, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.INTERNALS

    def is_equation(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a equation block.
        :return: True if declared in a equation block, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.EQUATION

    def is_local(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a local (e.g., update) block.
        :return: True if declared in a local block, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.LOCAL

    def is_input_buffer_current(self) -> bool:
        """
        Returns whether this variable symbol has been declared as a input-buffer current element.
        :return: True if input-buffer current, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.INPUT_BUFFER_CURRENT

    def is_input_buffer_spike(self) -> bool:
        """
        Returns whether this variable symbol has been declared as a input-buffer spike element.
        :return: True if input-buffer spike, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.INPUT_BUFFER_SPIKE

    def is_buffer(self) -> bool:
        """
        Returns whether this variable symbol represents a buffer or not.
        :return: True if buffer, otherwise False.
        :rtype: bool
        """
        return self.variable_type == VariableType.BUFFER

    def is_output(self) -> bool:
        """
        Returns whether this variable symbol has been declared as a output-buffer element.
        :return: True if output element, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.OUTPUT

    def is_kernel(self) -> bool:
        """
        Returns whether this variable belongs to the definition of a kernel.
        :return: True if part of a kernel definition, otherwise False.
        :rtype: bool
        """
        return self.variable_type == VariableType.KERNEL

    def is_init_values(self) -> bool:
        """
        Returns whether this variable belongs to the definition of a initial value.
        :return: True if part of a initial value, otherwise False.
        :rtype: bool
        """
        return self.block_type == BlockType.INITIAL_VALUES

    def print_symbol(self):
        if self.get_referenced_object() is not None:
            source_position = str(self.get_referenced_object().get_source_position())
        else:
            source_position = 'predefined'
        vector_value = self.get_vector_parameter() if self.has_vector_parameter() else 'none'
        typ_e = self.get_type_symbol().print_symbol()
        recordable = 'recordable, ' if self.is_recordable else ''
        func = 'function, ' if self.is_function else ''
        conductance_based = 'conductance based, ' if self.is_conductance_based else ''
        return 'VariableSymbol[' + self.get_symbol_name() + ', type=' \
               + typ_e + ', ' + str(self.block_type) + ', ' + recordable + func + conductance_based \
               + 'array parameter=' + vector_value + ', @' + source_position + ')'

    def get_type_symbol(self):
        """
        Returns the corresponding type symbol.
        :return: the current type symbol.
        :rtype: type_symbol
        """
        return copy(self.type_symbol)

    def set_type_symbol(self, type_symbol):
        """
        Updates the current type symbol to a new one.
        :param type_symbol: a new type symbol.
        :type type_symbol: type_symbol
        """
        self.type_symbol = type_symbol

    def is_ode_defined(self):
        """
        Returns whether this element is defined by a ode.
        :return: True if ode defined, otherwise False.
        :rtype: bool
        """
        return self.ode_or_kernel is not None and (isinstance(self.ode_or_kernel, ASTExpression)
                                                   or isinstance(self.ode_or_kernel, ASTSimpleExpression)
                                                   or isinstance(self.ode_or_kernel, ASTKernel)
                                                   or isinstance(self.ode_or_kernel, ASTOdeEquation))

    def get_ode_or_kernel(self):
        """
        Returns the ODE or kernel defining the value of this variable symbol.
        :return: the rhs defining the value.
        :rtype: ASTExpression or ASTSimpleExpression or ASTKernel
        """
        return self.ode_or_kernel

    def set_ode_or_kernel(self, expression):
        """
        Updates the currently stored ode-definition to the handed-over one.
        :param expression: a single rhs object.
        :type expression: ASTExpression
        """
        self.ode_or_kernel = expression

    def is_conductance_based(self) -> bool:
        """
        Indicates whether this element is conductance based, based on the physical units of the spike buffer. If the unit can be cast to Siemens, the function returns True, otherwise it returns False.

        :return: True if conductance based, otherwise False.
        """
        is_cond_based = self.type_symbol.is_castable_to(UnitTypeSymbol(unit=PredefinedUnits.get_unit("S")))
        is_curr_based = self.type_symbol.is_castable_to(UnitTypeSymbol(unit=PredefinedUnits.get_unit("A")))
        if is_cond_based == is_curr_based:
            code, message = Messages.get_could_not_determine_cond_based(
                type_str=self.type_symbol.print_nestml_type(), name=self.name)
            Logger.log_message(node=None, code=code, message=message, log_level=LoggingLevel.WARNING,
                               error_position=ASTSourceLocation.get_added_source_position())
            return False

        return is_cond_based

    def get_variable_type(self):
        """
        Returns the type of this variable.
        :return:  the type of the variable
        :rtype: VariableType
        """
        return self.variable_type

    def set_variable_type(self, v_type):
        """
        Updates the v_type of this variable symbol.
        :return: a single variable v_type
        :rtype: VariableType
        """
        self.variable_type = v_type

    def has_initial_value(self):
        """
        Returns whether this variable symbol has an initial value or not.
        :return: True if has initial value, otherwise False.
        :rtype: bool
        """
        return self.initial_value is not None and (isinstance(self.initial_value, ASTSimpleExpression)
                                                   or isinstance(self.initial_value, ASTExpression))

    def get_initial_value(self):
        """
        Returns the initial value of this variable symbol if one exists.
        :return: the initial value rhs.
        :rtype: ASTSimpleExpression or ASTExpression
        """
        return self.initial_value

    def set_initial_value(self, value):
        """
        Updates the initial value of this variable.
        :param value: a new initial value.
        :type value: ASTExpression or ASTSimpleExpression
        """
        self.initial_value = value

    def equals(self, other):
        """
        Compares the handed over object to this value-wise.
        :param other: the element to which this is compared to.
        :type other: Symbol or subclass
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        return (type(self) != type(other)
                and self.get_referenced_object() == other.get_referenced_object()
                and self.get_symbol_name() == other.get_symbol_name()
                and self.get_corresponding_scope() == other.get_corresponding_scope()
                and self.block_type == other.get_block_type()
                and self.get_vector_parameter() == other.get_vector_parameter()
                and self.declaring_expression == other.declaring_expression
                and self.is_predefined == other.is_predefined
                and self.is_function == other.is_function
                and self.is_conductance_based == other.is_conductance_based
                and self.is_recordable == other.is_recordable)

    def print_comment(self, prefix=None):
        """
        Prints the stored comment.
        :return: the corresponding comment.
        :rtype: str
        """
        ret = ''
        if not self.has_comment():
            return ''
        # in the last part, delete the new line if it is the last comment, otherwise there is an ugly gap
        # between the comment and the element
        for comment in self.get_comment():
            ret += (prefix if prefix is not None else '') + comment + \
                   ('\n' if self.get_comment().index(comment) < len(self.get_comment()) - 1 else '')
        return ret


class VariableType(Enum):
    """
    Indicates to which type of variable this is.
    """
    KERNEL = 0
    VARIABLE = 1
    BUFFER = 2
    EQUATION = 3
    TYPE = 4


class BlockType(Enum):
    """
    Indicates in which type of block this variable has been declared.
    """
    STATE = 1
    PARAMETERS = 2
    INTERNALS = 3
    INITIAL_VALUES = 4
    EQUATION = 5
    LOCAL = 6
    INPUT_BUFFER_CURRENT = 7
    INPUT_BUFFER_SPIKE = 8
    OUTPUT = 9
    PREDEFINED = 10
