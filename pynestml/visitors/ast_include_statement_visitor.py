# -*- coding: utf-8 -*-
#
# ast_include_statement_visitor.py
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

from typing import Optional

import os

from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_include_stmt import ASTIncludeStmt
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.string_type_symbol import StringTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import MessageCode, Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTIncludeStatementVisitor(ASTVisitor):
    """
    """

    def __init__(self, model_path: Optional[str]):
        super().__init__()
        self.model_path = model_path

    def visit_include_stmt(self, node: ASTIncludeStmt):
        self._handle_include_stmt(node)

    def visit_small_stmt(self, node: ASTSmallStmt):
        """
        :param expr: an expression
        """
        if node.is_include_stmt():
            self._handle_include_stmt(node.get_include_stmt())

    def _replace_statements(self, include_stmt, new_stmts):
        blk = include_stmt.get_parent()
        idx = blk.get_stmts().index(include_stmt)
        blk.get_stmts().pop(idx)
        blk.stmts = blk.stmts[:idx] + new_stmts + blk.stmts[idx:]
        for new_stmt in new_stmts:
            new_stmt.parent_ = blk
            blk.accept(ASTParentVisitor())

    def _handle_include_stmt(self, node: ASTIncludeStmt):
        filename = node.get_filename()
        if not os.path.isabs(filename):
            filename = os.path.join(self.model_path, filename)

        parsed_included_file = ModelParser.parse_included_file(filename)

        if isinstance(parsed_included_file, list):
            new_stmts = parsed_included_file
            include_stmt = node.get_parent().get_parent()

            if isinstance(include_stmt.get_parent(), ASTBlock):
                self._replace_statements(include_stmt, new_stmts)

            elif isinstance(node.get_parent().get_parent(), ASTEquationsBlock):
                print("not handled yet 4")
                assert False

        elif isinstance(parsed_included_file, ASTStmt):
            new_stmt = parsed_included_file
            include_stmt = node.get_parent().get_parent()

            if isinstance(include_stmt.get_parent(), ASTBlock):
                self._replace_statements(include_stmt, [new_stmt])

            # elif isinstance(node.get_parent().get_parent(), ASTEquationsBlock):
            else:
                print("not handled yet 1")
                assert False

        elif isinstance(parsed_included_file, ASTBlockWithVariables) or isinstance(parsed_included_file, ASTUpdateBlock) or isinstance(parsed_included_file, ASTEquationsBlock):
            new_blk = parsed_included_file
            if isinstance(node.get_parent(), ASTModelBody):
                idx = node.get_parent().get_body_elements().index(node)
                node.get_parent().body_elements[idx] = new_blk
                new_blk.parent_ = node
                node.accept(ASTParentVisitor())
                new_blk.accept(ASTParentVisitor())
            else:
                print("not handled yet 2")
                assert False

        else:
            assert False
