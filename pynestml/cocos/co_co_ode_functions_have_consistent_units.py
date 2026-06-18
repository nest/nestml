# -*- coding: utf-8 -*-
#
# co_co_ode_functions_have_consistent_units.py
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

from typing import Any, Dict, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoOdeFunctionsHaveConsistentUnits(CoCo):
    """
    This coco ensures that whenever an ODE function is defined, the physical unit of the left-hand side variable matches that of the right-hand side expression.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single model instance.
        """
        node.accept(OdeFunctionConsistentUnitsVisitor())


class OdeFunctionConsistentUnitsVisitor(ASTVisitor):

    def visit_ode_function(self, node):
        """
        Checks the coco.
        :param node: A single ode equation.
        :type node: ast_ode_equation
        """
        declared_type = node.get_data_type().type_symbol
        expression_type = node.get_expression().type
        if not expression_type.is_castable_to(declared_type):
            code, message = Messages.get_ode_function_needs_consistent_units(
                node.get_variable_name(), declared_type, expression_type)
            Logger.log_message(error_position=node.get_source_position(), code=code,
                               message=message, log_level=LoggingLevel.ERROR)
