# -*- coding: utf-8 -*-
#
# co_co_continuous_input_port_not_qualified.py
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
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoContinuousInputPortNotQualified(CoCo):
    """
    This coco ensures that continuous time input ports are not specified with a qualifier.
    Allowed:

    .. code-block:: nestml

       input:
           x nA <- continuous
       end

    Not allowed:

    .. code-block:: nestml

       input:
           x nA <- inhibitory continuous
       end
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(ContinuousPortQualifierSpecifiedVisitor())


class ContinuousPortQualifierSpecifiedVisitor(ASTVisitor):
    """
    This visitor ensures that continuous time input ports are not specified with an `inputQualifier`, e.g. excitatory, inhibitory.
    """

    def visit_input_port(self, node):
        if node.is_continuous() and node.has_input_qualifiers() and len(node.get_input_qualifiers()) > 0:
            qualifier_names = list((str(qualifier) for qualifier in node.get_input_qualifiers()))
            code, message = Messages.get_continuous_input_port_specified(node.get_name(), qualifier_names)
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.ERROR)
