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
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
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

    def visit_update_block(self, node: ASTUpdateBlock):
        """
        :param expr: an expression
        """
        print(node)

    def visit_small_stmt(self, node: ASTSmallStmt):
        """
        :param expr: an expression
        """
        if node.is_include_stmt():
            filename = node.get_include_stmt().get_filename()
            if not os.path.isabs(filename):
                filename = os.path.join(self.model_path, filename)

            parsed_included_file = ModelParser.parse_included_file(filename)

            if isinstance(parsed_included_file, list):
                new_stmts = parsed_included_file

                if isinstance(node.get_parent().get_parent(), ASTBlock):
                    blk = node.get_parent().get_parent()
                    idx = blk.get_stmts().index(node.get_parent())
                    blk.get_stmts().pop(idx)
                    blk.stmts = blk.stmts[:idx] + new_stmts + blk.stmts[idx:]
                    for new_stmt in new_stmts:
                        new_stmt.parent_ = blk
                        blk.accept(ASTParentVisitor())

                elif isinstance(node.get_parent().get_parent(), ASTEquationsBlock):
                    print("not handled yet")


            elif isinstance(parsed_included_file, ASTStmt):
                new_stmt = parsed_included_file

                if isinstance(node.get_parent().get_parent(), ASTBlock):
                    blk = node.get_parent().get_parent()
                    idx = blk.get_stmts().index(node.get_parent())
                    blk.get_stmts()[idx] = new_stmt
                    new_stmt.parent_ = blk
                    blk.accept(ASTParentVisitor())

                elif isinstance(node.get_parent().get_parent(), ASTEquationsBlock):
                    print("not handled yet")

            else:
                print("not handled yet!")
