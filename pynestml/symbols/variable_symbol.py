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
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import Symbol, SymbolKind
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


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
    COMMON_PARAMETERS = 3
    INTERNALS = 4
    EQUATION = 5
    LOCAL = 6
    INPUT = 7
    OUTPUT = 8
    PREDEFINED = 9


class VariableSymbol(Symbol):
    """
    This class is used to store a single variable symbol containing all required information.

    Attributes:
        block_type            The type of block in which this symbol has been declared. Type: BlockType
        vector_parameter      The parameter indicating the position in an array. Type: str
        delay_parameter       The parameter indicating the delay value for this variable. Type: str
        declaring_expression  The rhs defining the value of this symbol. Type: ASTExpression
        is_predefined         Indicates whether this symbol is predefined, e.g., t or e. Type: bool
        is_inline_expression  Indicates whether this symbol belongs to an inline expression. Type: bool
        is_recordable         Indicates whether this symbol belongs to a recordable element. Type: bool
        type_symbol           The concrete type of this variable.
        ode_declaration       Used to store the corresponding ode declaration.
        is_conductance_based  Indicates whether this buffer is conductance based.
        initial_value         Indicates the initial value if such is declared.
        variable_type         The type of the variable, either a kernel, or buffer or function. Type: VariableType
    """

    def __init__(self, element_reference=None, scope: Scope=None, name: str=None, block_type: BlockType=None,
                 vector_parameter: str=None, delay_parameter: str=None, declaring_expression: ASTExpression=None,
                 is_predefined: bool=False, is_inline_expression: bool=False, is_recordable: bool=False,
                 type_symbol: TypeSymbol=None, initial_value: ASTExpression=None, variable_type: VariableType=None,
                 decorators=None, namespace_decorators=None):
        """
        Standard constructor.
        :param element_reference: a reference to the first element where this type has been used/defined
        :param scope: the scope in which this type is defined in
        :param name: the name of the type symbol
        :param block_type: the type of block in which this element has been defined in
        :param vector_parameter: the parameter indicating a position in an array
        :param declaring_expression: a rhs declaring the value of this symbol.
        :param is_predefined: indicates whether this element represents a predefined variable, e.g., e or t
        :param is_inline_expression: Indicates whether this symbol belongs to an inline expression.
        :param is_recordable: indicates whether this elements is recordable or not.
        :param type_symbol: a type symbol representing the concrete type of this variable
        :param initial_value: the initial value if such an exists
        :param variable_type: the type of the variable
        :param decorators: a list of decorator keywords
        :type decorators list
        :param namespace_decorators a list of namespace decorators
        :type namespace_decorators list
        """
        super(VariableSymbol, self).__init__(element_reference=element_reference, scope=scope,
                                             name=name, symbol_kind=SymbolKind.VARIABLE)
        self.block_type = block_type
        self.vector_parameter = vector_parameter
        self.delay_parameter = delay_parameter
        self.declaring_expression = declaring_expression
        self.is_predefined = is_predefined
        self.is_inline_expression = is_inline_expression
        self.is_recordable = is_recordable
        self.type_symbol = type_symbol
        self.initial_value = initial_value
        self.variable_type = variable_type
        self.ode_or_kernel = None
        if decorators is None:
            decorators = []
        if namespace_decorators is None:
            namespace_decorators = {}
        self.decorators = decorators
        self.namespace_decorators = namespace_decorators

    def is_homogeneous(self):
        from pynestml.generated.PyNestMLLexer import PyNestMLLexer
        return PyNestMLLexer.DECORATOR_HOMOGENEOUS in self.decorators

    def has_decorators(self):
        return len(self.decorators) > 0

    def get_decorators(self):
        """
        Returns PyNESTMLLexer static variable codes
        """
        return self.decorators

    def get_namespace_decorators(self):
        return self.namespace_decorators

    def get_namespace_decorator(self, namespace):
        if namespace in self.namespace_decorators.keys():
            return self.namespace_decorators[namespace]
        return ''

    def has_vector_parameter(self):
        """
        Returns whether this variable symbol has a vector parameter.
        :return: True if vector parameter available, otherwise False.
        :rtype: bool
        """
        return self.vector_parameter is not None

    def has_delay_parameter(self):
        """
        Returns whether this variable has a delay value associated with it.
        :return: bool
        """
        return self.delay_parameter is not None and isinstance(self.delay_parameter, str)

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

    def get_delay_parameter(self):
        """
        Returns the delay value associated with this variable
        :return: the delay parameter
        """
        return self.delay_parameter

    def set_delay_parameter(self, delay):
        """
        Sets the delay value for this variable
        """
        self.delay_parameter = delay

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
        """
        return self.declaring_expression is not None and (isinstance(self.declaring_expression, ASTSimpleExpression)
                                                          or isinstance(self.declaring_expression, ASTExpression))

    def is_spike_input_port(self) -> bool:
        """
        Returns whether this symbol represents a spike input port.
        :return: True if spike input port, otherwise False.
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_spike()

    def is_continuous_input_port(self) -> bool:
        """
        Returns whether this symbol represents a continuous time input port.
        :return: True if continuous time input port, otherwise False.
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_continuous()

    def is_excitatory(self) -> bool:
        """
        Returns whether this symbol represents an input port with qualifier excitatory.
        :return: True if is excitatory, otherwise False.
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_excitatory()

    def is_inhibitory(self) -> bool:
        """
        Returns whether this symbol represents an input port with qualifier inhibitory.
        :return: True if is inhibitory, otherwise False.
        """
        return isinstance(self.get_referenced_object(), ASTInputPort) and self.get_referenced_object().is_inhibitory()

    def is_state(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a state block.
        :return: True if declared in a state block, otherwise False.
        """
        return self.block_type == BlockType.STATE

    def is_parameters(self) -> bool:
        """
        Returns whether this variable symbol has been declared in a parameters block.
        :return: True if declared in a parameters block, otherwise False.
        :rtype: bool
        """
        return self.block_type in [BlockType.PARAMETERS, BlockType.COMMON_PARAMETERS]

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

    def is_input(self) -> bool:
        """
        Returns whether this variable symbol has been declared as an input port.
        :return: True if input port, otherwise False.
        """
        return self.block_type == BlockType.INPUT

    def is_buffer(self) -> bool:
        """
        Returns whether this variable symbol represents a buffer or not.
        :return: True if buffer, otherwise False.
        """
        return self.variable_type == VariableType.BUFFER

    def is_output(self) -> bool:
        """
        Returns whether this variable symbol has been declared as output block element.
        :return: True if output element, otherwise False.
        """
        return self.block_type == BlockType.OUTPUT

    def is_kernel(self) -> bool:
        """
        Returns whether this variable belongs to the definition of a kernel.
        :return: True if part of a kernel definition, otherwise False.
        """
        return self.variable_type == VariableType.KERNEL

    def print_symbol(self):
        if self.get_referenced_object() is not None:
            source_position = str(self.get_referenced_object().get_source_position())
        else:
            source_position = 'predefined'
        vector_value = self.get_vector_parameter() if self.has_vector_parameter() else 'none'
        typ_e = self.get_type_symbol().print_symbol()
        recordable = 'recordable, ' if self.is_recordable else ''
        func = 'inline, ' if self.is_inline_expression else ''
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
        Indicates whether this element is conductance based, based on the physical units of the spike input port. If the unit can be cast to Siemens, the function returns True, otherwise it returns False.

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
        return (isinstance(other, type(self))
                and self.get_referenced_object() == other.get_referenced_object()
                and self.get_symbol_name() == other.get_symbol_name()
                and self.get_corresponding_scope() == other.get_corresponding_scope()
                and self.block_type == other.get_block_type()
                and self.get_vector_parameter() == other.get_vector_parameter()
                and self.declaring_expression == other.declaring_expression
                and self.is_predefined == other.is_predefined
                and self.is_inline_expression == other.is_inline_expression
                and self.is_conductance_based == other.is_conductance_based
                and self.is_recordable == other.is_recordable)

    def print_comment(self, prefix: str = "") -> str:
        """
        Prints the stored comment.
        :return: the corresponding comment.
        """
        ret = ''
        if not self.has_comment():
            return ''
        # in the last part, delete the new line if it is the last comment, otherwise there is an ugly gap
        # between the comment and the element
        for comment in self.get_comment():
            ret += prefix + comment + ('\n' if self.get_comment().index(comment) < len(self.get_comment()) - 1 else '')
        return ret
