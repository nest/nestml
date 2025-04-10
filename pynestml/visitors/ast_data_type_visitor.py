# -*- coding: utf-8 -*-
#
# ast_data_type_visitor.py
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

from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_unit_type_visitor import ASTUnitTypeVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTDataTypeVisitor(ASTVisitor):
    """
    This class represents a visitor which inspects a handed over data type, checks if correct typing has been used
    (e.g., no computation between primitive and non primitive data types etc.) and finally updates the type symbols
    of the datatype meta_model.
    """

    def __init__(self):
        super(ASTDataTypeVisitor, self).__init__()
        self.symbol = None
        self.result = None

    def visit_data_type(self, node):
        """
        Visits a single data type meta_model node and updates, checks correctness and updates its type symbol.
        This visitor can also be used to derive the original name of the unit.
        :param node: a single datatype node.
        :type node: ast_data_type
        """
        if node.is_integer:
            self.symbol = PredefinedTypes.get_integer_type()
            node.set_type_symbol(self.symbol)
        elif node.is_real:
            self.symbol = PredefinedTypes.get_real_type()
            node.set_type_symbol(self.symbol)
        elif node.is_string:
            self.symbol = PredefinedTypes.get_string_type()
            node.set_type_symbol(self.symbol)
        elif node.is_boolean:
            self.symbol = PredefinedTypes.get_boolean_type()
            node.set_type_symbol(self.symbol)
        elif node.is_void:
            self.symbol = PredefinedTypes.get_void_type()
            node.set_type_symbol(self.symbol)
        elif node.is_unit_type:
            unit_type_visitor = ASTUnitTypeVisitor()
            node.get_unit_type().accept(unit_type_visitor)
            self.symbol = unit_type_visitor.symbol
            node.set_type_symbol(self.symbol)

    def endvisit_data_type(self, node):
        if node.is_unit_type() and node.get_unit_type().get_type_symbol() is not None:
            node.set_type_symbol(node.get_unit_type().get_type_symbol())
        if self.symbol is not None:
            self.result = self.symbol.get_symbol_name()
        else:
            code, message = Messages.astdatatype_type_symbol_could_not_be_derived()
            Logger.log_message(None, code, message, node.get_source_position(), LoggingLevel.ERROR)
            return
