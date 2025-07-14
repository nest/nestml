# -*- coding: utf-8 -*-
#
# inline_expression_expansion_transformer.py
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

from typing import List, Optional, Mapping, Any, Union, Sequence

import re

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


class InlineExpressionExpansionTransformer(Transformer):
    r"""
    Make inline expressions self contained, i.e. without any references to other inline expressions.

    Additionally, replace variable symbols referencing inline expressions in defining expressions of ODEs with the corresponding defining expressions from the inline expressions.
    """

    _variable_matching_template = r'(\b)({})(\b)'

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        single = False
        if isinstance(models, ASTNode):
            single = True
            models = [models]

        for model in models:
            if not model.get_equations_blocks():
                continue

            for equations_block in model.get_equations_blocks():
                self.make_inline_expressions_self_contained(equations_block.get_inline_expressions())

            for equations_block in model.get_equations_blocks():
                self.replace_inline_expressions_through_defining_expressions(equations_block.get_ode_equations(), equations_block.get_inline_expressions())

        if single:
            return models[0]

        return models

    def make_inline_expressions_self_contained(self, inline_expressions: List[ASTInlineExpression]) -> List[ASTInlineExpression]:
        r"""
        Make inline expressions self contained, i.e. without any references to other inline expressions.

        :param inline_expressions: A sorted list with entries ASTInlineExpression.
        :return: A list with ASTInlineExpressions. Defining expressions don't depend on each other.
        """
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        for source in inline_expressions:
            source_position = source.get_source_position()
            for target in inline_expressions:
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                old_parent = target.expression.parent_
                target.expression = ModelParser.parse_expression(target_definition)
                target.expression.update_scope(source.get_scope())
                target.expression.parent_ = old_parent
                target.expression.accept(ASTParentVisitor())
                target.expression.accept(ASTSymbolTableVisitor())

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return inline_expressions

    @classmethod
    def replace_inline_expressions_through_defining_expressions(self, definitions: Sequence[ASTOdeEquation],
                                                                inline_expressions: Sequence[ASTInlineExpression]) -> Sequence[ASTOdeEquation]:
        r"""
        Replace variable symbols referencing inline expressions in defining expressions of ODEs with the corresponding defining expressions from the inline expressions.

        :param definitions: A list of ODE definitions (**updated in-place**).
        :param inline_expressions: A list of inline expression definitions.
        :return: A list of updated ODE definitions (same as the ``definitions`` parameter).
        """
        from pynestml.utils.model_parser import ModelParser
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        for m in inline_expressions:
            if "mechanism" not in [e.namespace for e in m.get_decorators()]:
                """
                exclude compartmental mechanism definitions in order to have the
                inline as a barrier inbetween odes that are meant to be solved independently
                """
                source_position = m.get_source_position()
                for target in definitions:
                    matcher = re.compile(self._variable_matching_template.format(m.get_variable_name()))
                    target_definition = str(target.get_rhs())
                    target_definition = re.sub(matcher, "(" + str(m.get_expression()) + ")", target_definition)
                    old_parent = target.rhs.parent_
                    target.rhs = ModelParser.parse_expression(target_definition)
                    target.update_scope(m.get_scope())
                    target.rhs.parent_ = old_parent
                    target.rhs.accept(ASTParentVisitor())
                    target.accept(ASTSymbolTableVisitor())

                    def log_set_source_position(node):
                        if node.get_source_position().is_added_source_position():
                            node.set_source_position(source_position)

                    target.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return definitions
