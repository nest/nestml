# -*- coding: utf-8 -*-
#
# co_co_quantities_valid.py
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
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.predefined_quantities import InvalidQuantityException, PredefinedQuantities
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoQuantitiesValid(CoCo):
    r"""
    This coco ensures that all physical quantities used as data types (for instance ``"voltage"`` or ``"conductance / time"``) are known and well-formed.

    Allowed:

    .. code-block:: nestml

       V_m "voltage" = -70 mV
       k "1 / time" = 1 / ms

    Not allowed:

    .. code-block:: nestml

       V_m "voltaeg" = -70 mV      # unknown quantity
       k "2 / time" = 1 / ms       # numeric numerator must be 1
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        node.accept(QuantitiesValidVisitor())


class QuantitiesValidVisitor(ASTVisitor):
    """
    Visits data types and checks that quantities can be interpreted.
    """

    def visit_data_type(self, node: ASTDataType):
        if not node.is_quantity():
            return

        try:
            PredefinedQuantities.parse(node.get_quantity())
        except InvalidQuantityException as e:
            Logger.log_message(code=e.code, message=e.message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
