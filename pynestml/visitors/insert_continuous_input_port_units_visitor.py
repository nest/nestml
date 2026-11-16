# -*- coding: utf-8 -*-
#
# insert_continuous_input_port_units_visitor.py
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

from typing import List

from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class InsertContinuousInputPortUnitsVisitor(ASTVisitor):
    r"""
    The value arriving at a continuous input port is a plain number, which is interpreted in the unit given in the port declaration. For instance, given

    .. code-block:: nestml

       input:
           I_stim pA <- continuous

    the number arriving at ``I_stim`` is to be interpreted as a current in pA. As variables are typed by physical quantity (which does not imply any particular unit), this conversion factor is made explicit in the model: every reference to the port is multiplied by the unit of the port, so that for example

    .. code-block:: nestml

       V_m' = -V_m / tau_m + I_stim / C_m

    becomes

    .. code-block:: nestml

       V_m' = -V_m / tau_m + (I_stim * 1 pA) / C_m

    Accordingly, the port variable ``I_stim`` itself is of type real (see ``ASTSymbolTableVisitor.endvisit_input_port()``), and the expression ``(I_stim * 1 pA)`` is of the physical type "current".

    Continuous input ports declared with a primitive data type (such as ``real``) are left unchanged.
    """

    def __init__(self):
        super().__init__()
        self._port_references: List[ASTSimpleExpression] = []

    @classmethod
    def insert_units(cls, model: ASTModel) -> None:
        r"""
        Insert the units of continuous input ports in all expressions in the given model. Assumes that the symbol table and parent pointers are up to date.
        """
        visitor = InsertContinuousInputPortUnitsVisitor()
        model.accept(visitor)

        if not visitor._port_references:
            return

        for node in visitor._port_references:
            cls._insert_unit(node)

        model.accept(ASTParentVisitor())
        model.accept(ASTSymbolTableVisitor())

    def visit_simple_expression(self, node: ASTSimpleExpression) -> None:
        if not node.is_variable() or node.get_scope() is None:
            return

        symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
        if symbol is None:
            return

        port = symbol.get_referenced_object()
        if isinstance(port, ASTInputPort) and port.is_continuous() and port.has_datatype() and port.get_datatype().is_unit_type():
            self._port_references.append(node)

    @classmethod
    def _insert_unit(cls, node: ASTSimpleExpression) -> None:
        from pynestml.utils.model_parser import ModelParser

        port = node.get_scope().resolve_to_symbol(node.get_variable().get_name(), SymbolKind.VARIABLE).get_referenced_object()
        parent = node.get_parent()

        # construct the expression ``(port * 1 unit)``, and then put the original reference to the port in place
        new_node = ModelParser.parse_expression("(__port * 1 " + str(port.get_datatype().get_unit_type()) + ")")
        product = new_node.get_expression()
        product.lhs = node

        for n in [new_node, product, product.get_rhs()]:
            n.update_scope(node.get_scope())
            n.set_source_position(node.get_source_position())

        cls._replace_child(parent, node, new_node)

        # cached types of the enclosing expressions are now outdated
        ancestor = parent
        while ancestor is not None:
            if isinstance(ancestor, ASTExpressionNode):
                ancestor.type = None

            ancestor = ancestor.parent_ if "parent_" in dir(ancestor) else None

    @staticmethod
    def _replace_child(parent: ASTNode, old: ASTNode, new: ASTNode) -> None:
        for attr, value in vars(parent).items():
            if attr == "parent_":
                continue

            if value is old:
                setattr(parent, attr, new)
                return

            if isinstance(value, list):
                for i, item in enumerate(value):
                    if item is old:
                        value[i] = new
                        return

        raise RuntimeError("Could not find node \"" + str(old) + "\" among the children of \"" + str(parent) + "\"")
