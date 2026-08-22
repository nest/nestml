# -*- coding: utf-8 -*-
#
# co_co_no_solitary_physical_units.py
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

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from typing import Any, Dict, Optional

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNoSolitaryPhysicalUnits(CoCo):
    """
    This coco checks that there are no free-standing physical units.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        node.accept(NoSolitaryPhysicalUnitsVisitor())


class NoSolitaryPhysicalUnitsVisitor(ASTVisitor):
    def visit_variable(self, node: ASTVariable):
        symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
        if symbol is None:
            # test if variable name can be resolved to a type
            if PredefinedUnits.is_unit(node.get_complete_name()):
                code, message = Messages.get_no_solitary_physical_units_allowed(node.get_complete_name())
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
