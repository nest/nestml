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

from typing import Any, List, Optional, Union

from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.utils.port_signal_type import PortSignalType


class ASTInputPort(ASTNode):
    r"""
    This class is used to store a declaration of an input port.
    ASTInputPort represents a single input port, e.g.:

    .. code-block:: nestml

       spike_in <- spike(weight real)

    @attribute name: The name of the input port.
    @attribute sizeParameter: Optional size parameter for multisynapse neuron.
    @attribute datatype: Optional data type of the port.
    @attribute isSpike: Indicates that this input port accepts spikes.
    @attribute isContinuous: Indicates that this input port accepts continuous time input.
    """

    def __init__(self,
                 name: str,
                 signal_type: PortSignalType,
                 parameters: Optional[List[ASTParameter]] = None,
                 size_parameter: Optional[Union[ASTSimpleExpression, ASTExpression]] = None,
                 data_type: Optional[ASTDataType] = None,
                 *args, **kwargs):
        r"""
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the port
        :param signal_type: type of signal received, i.e., spikes or continuous
        :param parameters: spike event parameters (for instance, ``foo ms`` in ``spike_in_port <- spike(foo ms)``)
        :param size_parameter: a parameter indicating the index in an array.
        :param data_type: the data type of this input port
        """
        super(ASTInputPort, self).__init__(*args, **kwargs)
        self.name = name
        self.signal_type = signal_type
        self.size_parameter = size_parameter
        self.data_type = data_type
        self.parameters = parameters

    def clone(self) -> ASTInputPort:
        r"""
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        data_type_dup = None
        if self.data_type:
            data_type_dup = self.data_type.clone()
        parameters_dup = None
        if self.parameters:
            parameters_dup = [parameter.clone() for parameter in self.parameters]
        dup = ASTInputPort(name=self.name,
                           signal_type=self.signal_type,
                           parameters=parameters_dup,
                           size_parameter=self.size_parameter,
                           data_type=data_type_dup,
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

    def get_parameters(self) -> List[ASTParameter]:
        r"""
        Returns the parameters of the declared input port.
        :return: the parameters.
        """
        if self.parameters is not None:
            return self.parameters

        return []

    def has_size_parameter(self) -> bool:
        r"""
        Returns whether a size parameter has been defined.
        :return: True if size has been used, otherwise False.
        """
        return self.size_parameter is not None

    def get_size_parameter(self) -> Optional[Union[ASTSimpleExpression, ASTExpression]]:
        r"""
        Returns the size parameter.
        :return: the size parameter.
        """
        return self.size_parameter

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

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        children = []
        if self.has_datatype():
            children.append(self.get_datatype())

        if self.get_size_parameter():
            children.append(self.get_size_parameter())

        return children

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTInputPort):
            return False

        if self.get_name() != other.get_name():
            return False

        if self.has_size_parameter() + other.has_size_parameter() == 1:
            return False

        if (self.has_size_parameter() and other.has_size_parameter()
                and self.get_size_parameter() != other.get_size_parameter()):
            return False

        if self.has_datatype() + other.has_datatype() == 1:
            return False

        if self.has_datatype() and other.has_datatype() and not self.get_datatype().equals(other.get_datatype()):
            return False

        return self.is_spike() == other.is_spike() and self.is_continuous() == other.is_continuous()
