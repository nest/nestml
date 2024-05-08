# -*- coding: utf-8 -*-
#
# ast_parent_visitor.py
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

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_namespace_decorator import ASTNamespaceDecorator
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbol_table.scope import Scope, ScopeType
from pynestml.symbols.function_symbol import FunctionSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol, BlockType, VariableType
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.stack import Stack
from pynestml.visitors.ast_data_type_visitor import ASTDataTypeVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTParentVisitor(ASTVisitor):
    r"""
    For each node in the AST, assign its ``parent_`` attribute; in other words, make it a doubly-linked tree.
    """

    def __init__(self):
        super(ASTParentVisitor, self).__init__()

    def visit(self, node: ASTNode):
        r"""Set ``parent_`` property on all children to refer back to this node."""
        children = node.get_children()
        for child in children:
            child.parent_ = node
        # queue = [node]
        # while queue:
        #     node = queue.pop(0)   # pop from the front of the queue -- breadth first search

        #     children = node.get_children()
        #     for child in children:
        #         child.parent_ = node

        #     queue.extend(children)
