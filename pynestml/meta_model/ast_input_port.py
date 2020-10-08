# -*- coding: utf-8 -*-
#
# ast_input_port.py
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

from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.port_signal_type import PortSignalType


class ASTInputPort(ASTNode):
    """
    This class is used to store a declaration of an input port.
    ASTInputPort represents a single input port, e.g.:
      spikeBuffer type <- excitatory spike

    @attribute name: The name of the input port.
    @attribute sizeParameter: Optional size parameter for multisynapse neuron.
    @attribute datatype: Optional data type of the buffer.
    @attribute inputQualifier: The qualifier keyword of the input port, to indicate e.g. inhibitory-only or excitatory-only spiking inputs on this port.
    @attribute isSpike: Indicates that this input port accepts spikes.
    @attribute isCurrent: Indicates that this input port accepts current generator input.

    Grammar:
        inputPort:
            name=NAME
            (LEFT_SQUARE_BRACKET sizeParameter=NAME RIGHT_SQUARE_BRACKET)?
            (dataType)?
            LEFT_ANGLE_MINUS inputQualifier*
            (isCurrent = CURRENT_KEYWORD | isSpike = SPIKE_KEYWORD);

    """

    def __init__(self, name=None, size_parameter=None, data_type=None, input_qualifiers=None, signal_type=None,
                 *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the port
        :type name: str
        :param size_parameter: a parameter indicating the index in an array.
        :type size_parameter: str
        :param data_type: the data type of this buffer
        :type data_type: ASTDataType
        :param input_qualifiers: a list of input qualifiers for this port.
        :type input_qualifiers: list(ASTInputQualifier)
        :param signal_type: type of signal received, i.e., spikes or currents
        :type signal_type: SignalType
        """
        super(ASTInputPort, self).__init__(*args, **kwargs)
        assert name is not None and isinstance(name, str), \
            '(PyNestML.ASTInputPort) No or wrong type of name provided (%s)!' % type(name)
        assert signal_type is not None and isinstance(signal_type, PortSignalType), \
            '(PyNestML.ASTInputPort) No or wrong type of input signal type provided (%s)!' % type(signal_type)
        if input_qualifiers is None:
            input_qualifiers = []
        assert input_qualifiers is not None and isinstance(input_qualifiers, list), \
            '(PyNestML.ASTInputPort) No or wrong type of input qualifiers provided (%s)!' % type(input_qualifiers)
        for qual in input_qualifiers:
            assert qual is not None and isinstance(qual, ASTInputQualifier), \
                '(PyNestML.ASTInputPort) No or wrong type of input qualifier provided (%s)!' % type(qual)
        assert size_parameter is None or isinstance(size_parameter, str), \
            '(PyNestML.ASTInputPort) Wrong type of index parameter provided (%s)!' % type(size_parameter)
        assert data_type is None or isinstance(data_type, ASTDataType), \
            '(PyNestML.ASTInputPort) Wrong type of data-type provided (%s)!' % type(data_type)
        self.signal_type = signal_type
        self.input_qualifiers = input_qualifiers
        self.size_parameter = size_parameter
        self.name = name
        self.data_type = data_type

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTInputPort
        """
        data_type_dup = None
        if self.data_type:
            data_type_dup = self.data_type.clone()
        dup = ASTInputPort(name=self.name,
                           size_parameter=self.size_parameter,
                           data_type=data_type_dup,
                           input_qualifiers=[input_qualifier.clone() for input_qualifier in self.input_qualifiers],
                           signal_type=self.signal_type,
                           # ASTNode common attributes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           post_comments=[s for s in self.post_comments],
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_name(self):
        """
        Returns the name of the declared buffer.
        :return: the name.
        :rtype: str
        """
        return self.name

    def has_index_parameter(self):
        """
        Returns whether a index parameter has been defined.
        :return: True if index has been used, otherwise False.
        :rtype: bool
        """
        return self.size_parameter is not None

    def get_index_parameter(self):
        """
        Returns the index parameter.
        :return: the index parameter.
        :rtype: str
        """
        return self.size_parameter

    def has_input_qualifiers(self):
        """
        Returns whether input qualifiers have been defined.
        :return: True, if at least one input qualifier has been defined.
        :rtype: bool
        """
        return len(self.input_qualifiers) > 0

    def get_input_qualifiers(self):
        """
        Returns the list of input qualifiers.
        :return: a list of input qualifiers.
        :rtype: list(ASTInputQualifier)
        """
        return self.input_qualifiers

    def is_spike(self):
        """
        Returns whether this is a spike buffer or not.
        :return: True if spike buffer, False else.
        :rtype: bool
        """
        return self.signal_type is PortSignalType.SPIKE

    def is_current(self):
        """
        Returns whether this is a current buffer or not.
        :return: True if current buffer, False else.
        :rtype: bool
        """
        return self.signal_type is PortSignalType.CURRENT

    def is_excitatory(self):
        """
        Returns whether this buffer is excitatory or not. For this, it has to be marked explicitly by the
        excitatory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if excitatory, False otherwise.
        :rtype: bool
        """
        if self.get_input_qualifiers() is not None and len(self.get_input_qualifiers()) == 0:
            return True
        for in_type in self.get_input_qualifiers():
            if in_type.is_excitatory:
                return True
        return False

    def is_inhibitory(self):
        """
        Returns whether this buffer is inhibitory or not. For this, it has to be marked explicitly by the
        inhibitory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if inhibitory, False otherwise.
        :rtype: bool
        """
        if self.get_input_qualifiers() is not None and len(self.get_input_qualifiers()) == 0:
            return True
        for in_type in self.get_input_qualifiers():
            if in_type.is_inhibitory:
                return True
        return False

    def has_datatype(self):
        """
        Returns whether this buffer has a defined data type or not.
        :return: True if it has a datatype, otherwise False.
        :rtype: bool
        """
        return self.data_type is not None and isinstance(self.data_type, ASTDataType)

    def get_datatype(self):
        """
        Returns the currently used data type of this buffer.
        :return: a single data type object.
        :rtype: ASTDataType
        """
        return self.data_type

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.has_datatype():
            if self.get_datatype() is ast:
                return self
            if self.get_datatype().get_parent(ast) is not None:
                return self.get_datatype().get_parent(ast)
        for qual in self.get_input_qualifiers():
            if qual is ast:
                return self
            if qual.get_parent(ast) is not None:
                return qual.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal,otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInputPort):
            return False
        if self.get_name() != other.get_name():
            return False
        if self.has_index_parameter() + other.has_index_parameter() == 1:
            return False
        if (self.has_index_parameter() and other.has_index_parameter()
                and self.get_input_qualifiers() != other.get_index_parameter()):
            return False
        if self.has_datatype() + other.has_datatype() == 1:
            return False
        if self.has_datatype() and other.has_datatype() and not self.get_datatype().equals(other.get_datatype()):
            return False
        if len(self.get_input_qualifiers()) != len(other.get_input_qualifiers()):
            return False
        my_input_qualifiers = self.get_input_qualifiers()
        your_input_qualifiers = other.get_input_qualifiers()
        for i in range(0, len(my_input_qualifiers)):
            if not my_input_qualifiers[i].equals(your_input_qualifiers[i]):
                return False
        return self.is_spike() == other.is_spike() and self.is_current() == other.is_current()
