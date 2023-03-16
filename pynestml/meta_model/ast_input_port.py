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

from __future__ import annotations

from typing import Any, List, Optional

from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.port_signal_type import PortSignalType


class ASTInputPort(ASTNode):
    r"""
    This class is used to store a declaration of an input port.
    ASTInputPort represents a single input port, e.g.:

    .. code-block:: nestml

       spike_in pA <- excitatory spike

    @attribute name: The name of the input port.
    @attribute sizeParameter: Optional size parameter for multisynapse neuron.
    @attribute datatype: Optional data type of the port.
    @attribute inputQualifier: The qualifier keyword of the input port, to indicate e.g. inhibitory-only or excitatory-only spiking inputs on this port.
    @attribute isSpike: Indicates that this input port accepts spikes.
    @attribute isContinuous: Indicates that this input port accepts continuous time input.

    Grammar:
        inputPort:
            name=NAME
            (LEFT_SQUARE_BRACKET sizeParameter=NAME RIGHT_SQUARE_BRACKET)?
            (dataType)?
            LEFT_ANGLE_MINUS inputQualifier*
            (isContinuous = CONTINUOUS_KEYWORD | isSpike = SPIKE_KEYWORD);

    """

    def __init__(self,
                 name: str,
                 signal_type: PortSignalType,
                 size_parameter: Optional[str] = None,
                 data_type: Optional[ASTDataType] = None,
                 input_qualifiers: Optional[List[ASTInputQualifier]] = None,
                 *args, **kwargs):
        r"""
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the port
        :param size_parameter: a parameter indicating the index in an array.
        :param data_type: the data type of this input port
        :param input_qualifiers: a list of input qualifiers for this port.
        :param signal_type: type of signal received, i.e., spikes or continuous
        """
        super(ASTInputPort, self).__init__(*args, **kwargs)
        if input_qualifiers is None:
            input_qualifiers = []
        self.name = name
        self.signal_type = signal_type
        self.size_parameter = size_parameter
        self.data_type = data_type
        self.input_qualifiers = input_qualifiers

    def clone(self) -> ASTInputPort:
        r"""
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        data_type_dup = None
        if self.data_type:
            data_type_dup = self.data_type.clone()
        dup = ASTInputPort(name=self.name,
                           signal_type=self.signal_type,
                           size_parameter=self.size_parameter,
                           data_type=data_type_dup,
                           input_qualifiers=[input_qualifier.clone() for input_qualifier in self.input_qualifiers],
                           # ASTNode common attributes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_name(self) -> str:
        r"""
        Returns the name of the declared input port.
        :return: the name.
        """
        return self.name

    def has_size_parameter(self) -> bool:
        r"""
        Returns whether a size parameter has been defined.
        :return: True if size has been used, otherwise False.
        """
        return self.size_parameter is not None

    def get_size_parameter(self) -> str:
        r"""
        Returns the size parameter.
        :return: the size parameter.
        """
        return self.size_parameter

    def has_input_qualifiers(self) -> bool:
        r"""
        Returns whether input qualifiers have been defined.
        :return: True, if at least one input qualifier has been defined.
        """
        return len(self.input_qualifiers) > 0

    def get_input_qualifiers(self) -> List[ASTInputQualifier]:
        r"""
        Returns the list of input qualifiers.
        :return: a list of input qualifiers.
        """
        return self.input_qualifiers

    def is_spike(self) -> bool:
        r"""
        Returns whether this is a spiking input port or not.
        :return: True if spike input port, False otherwise.
        """
        return self.signal_type is PortSignalType.SPIKE

    def is_continuous(self) -> bool:
        r"""
        Returns whether this is a continous time port or not.
        :return: True if continuous time, False otherwise.
        """
        return self.signal_type is PortSignalType.CONTINUOUS

    def is_excitatory(self) -> bool:
        r"""
        Returns whether this port is excitatory or not. For this, it has to be marked explicitly by the
        excitatory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if excitatory, False otherwise.
        """
        if self.get_input_qualifiers() is not None and len(self.get_input_qualifiers()) == 0:
            return True
        for in_type in self.get_input_qualifiers():
            if in_type.is_excitatory:
                return True
        return False

    def is_inhibitory(self) -> bool:
        r"""
        Returns whether this port is inhibitory or not. For this, it has to be marked explicitly by the
        inhibitory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if inhibitory, False otherwise.
        """
        if self.get_input_qualifiers() is not None and len(self.get_input_qualifiers()) == 0:
            return True
        for in_type in self.get_input_qualifiers():
            if in_type.is_inhibitory:
                return True
        return False

    def has_datatype(self):
        r"""
        Returns whether this port has a defined data type or not.
        :return: True if it has a datatype, otherwise False.
        """
        return self.data_type is not None and isinstance(self.data_type, ASTDataType)

    def get_datatype(self) -> ASTDataType:
        r"""
        Returns the currently used data type of this port.
        :return: a single data type object.
        """
        return self.data_type

    def get_parent(self, ast: ASTNode) -> Optional[ASTNode]:
        r"""
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :return: AST if this or one of the child nodes contains the handed over element.
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

    def equals(self, other: Any) -> bool:
        r"""
        The equals method.
        :param other: a different object.
        :return: True if equal,otherwise False.
        """
        if not isinstance(other, ASTInputPort):
            return False
        if self.get_name() != other.get_name():
            return False
        if self.has_size_parameter() + other.has_size_parameter() == 1:
            return False
        if (self.has_size_parameter() and other.has_size_parameter()
                and self.get_input_qualifiers() != other.get_size_parameter()):
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
        return self.is_spike() == other.is_spike() and self.is_continuous() == other.is_continuous()
