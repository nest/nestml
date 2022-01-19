# -*- coding: utf-8 -*-
#
# co_co_continuous_input_port_qualifiers.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.port_qualifier_type import PortQualifierType
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoContinuousInputPortQualifiers(CoCo):
    r"""
    This coco ensures that continuous time input ports may only be specified with the `post` qualifier.

    Allowed:

    .. code-block:: nestml

       input:
           x nA <- continuous
       end

    .. code-block:: nestml

       input:
           x nA <- post continuous
       end

    Not allowed:

    .. code-block:: nestml

       input:
           x nA <- inhibitory continuous
       end
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuronOrSynapse) -> None:
        r"""
        Ensures the coco for the handed over node.
        :param node: a neuron or synapse
        """
        node.accept(ContinuousPortQualifierSpecifiedVisitor())


class ContinuousPortQualifierSpecifiedVisitor(ASTVisitor):
    r"""
    This visitor ensures that continuous time input ports are specified with a valid qualifier. Currently only `post` is supported.
    """

    def visit_input_port(self, node: ASTNode) -> None:
        if node.is_continuous() and node.has_qualifiers() and len(node.get_qualifiers()) > 0:
            for qual in node.get_qualifiers():
                if not qual.get_qualifier_type() is PortQualifierType.POST:
                    code, message = Messages.get_continuous_input_port_specified(node.get_name(),
                                                                                 qual.get_qualifier_type().name)
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.ERROR)
