# -*- coding: utf-8 -*-
#
# variable_name_rewriter.py
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

from __future__ import annotations

from typing import Any, Callable, List, Mapping, Optional, Sequence

from pynestml.meta_model.ast_node import ASTNode
from pynestml.transformers.transformer import Transformer
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.with_options import WithOptions
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor

from abc import ABCMeta, abstractmethod
import copy


class VariableNameRewriter(Transformer):
    r"""Perform a model transformation step, for instance, rewriting disallowed variable names like "lambda" because it conflicts with a keyword."""

    _default_options = {
        "forbidden_names": [],
        "strategy": "append_underscores"
    }

    fix_name_func_: Callable[[str], str]
    rewritten_names_: List[Tuple[str, str]]

    class VariableNameRewriterVisitor(ASTVisitor):
        forbidden_names_: List[str]
        fix_name_func_: Callable[[str], str]

        def __init__(self, forbidden_names: List[str], fix_name_func: Callable[[str], str]):
            super().__init__()
            self.forbidden_names_ = forbidden_names
            self.fix_name_func_ = fix_name_func

        def visit_simple_expression(self, node):
            if node.is_variable():
                var = node.get_variable()
                if var.get_name() in self.forbidden_names_:
                    var.set_name(self.fix_name_func_(var.get_name()))

        def visit_declaration(self, node):
            for var in node.get_variables():
                if var.get_name() in self.forbidden_names_:
                    var.set_name(self.fix_name_func_(var.get_name()))

        def visit_assignment(self, node):
            var = node.get_variable()
            if var.get_name() in self.forbidden_names_:
                var.set_name(self.fix_name_func_(var.get_name()))

        def visit_expression(self, node):
            for var in node.get_variables():
                if var.get_name() in self.forbidden_names_:
                    var.set_name(self.fix_name_func_(var.get_name()))

        def visit_ode_equation(self, node):
            var = node.lhs
            if var.get_name() in self.forbidden_names_:
                var.set_name(self.fix_name_func_(var.get_name()))

    def __init__(self, options: Optional[Mapping[str, Any]]=None):
        super(Transformer, self).__init__(options)
        if self.get_option("strategy") == "append_underscores":
            self.fix_name_func_ = self.fix_name_append_underscores_
        else:
            raise Exception("Unknown strategy: \"" + self.get_option("strategy") + "\"")
        self.rewritten_names_ = []

    def fix_name_append_underscores_(self, name: str) -> str:
        name_orig = name
        while name in self.get_option("forbidden_names"):
            name += "_"

        if not name == name_orig and not (name, name_orig) in self.rewritten_names_:
            self.rewritten_names_.append((name, name_orig))
            msg = "Rewrote variable \"" + name_orig + "\" to \"" + name + "\""
            Logger.log_message(None, None, msg, None, LoggingLevel.INFO)

        return name

    def transform(self, model: ASTNode) -> ASTNode:
        model.accept(self.VariableNameRewriterVisitor(self.get_option("forbidden_names"), self.fix_name_func_))
        model.accept(ASTSymbolTableVisitor())

        return model
