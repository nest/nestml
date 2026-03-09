# -*- coding: utf-8 -*-
#
# replace_sift_with_buffer_transformer.py
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

from typing import Callable, List, Optional, Mapping, Any, Union, Sequence
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.transformers.transformer import Transformer
from pynestml.visitors.ast_visitor import ASTVisitor


class ReplaceSiftWithBufferTransformer(Transformer):
    r"""
    Replace occurrences of ``sift(spike_in_port, t)`` with ``spike_in_port`` for code generation.
    """

    class SiftRewriterVisitor(ASTVisitor):
        def visit_function_call(self, node: ASTFunctionCall):
            if node.get_name() == PredefinedFunctions.SIFT:
                parent = node.get_parent()
                # binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True)
                # prefactor = ASTNodeFactory.create_ast_simple_expression(numeric_literal=node.args[0].get_implicit_conversion_factor())
                # node.args[0].implicit_conversion_factor = 1
                # new_node = ASTExpression(binary_operator=binary_operator, lhs=prefactor, rhs=node.args[0])

                # if parent.get_parent().rhs == parent:
                #     parent.get_parent().rhs = new_node
                # else:
                #     assert parent.get_parent().lhs == parent
                #     parent.get_parent().lhs = new_node

                # import pdb;pdb.set_trace()
                parent.function_call = None
                parent.variable = node.args[0].variable
                parent.variable.parent = parent
                parent.implicit_conversion_factor = node.args[0].get_implicit_conversion_factor()

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        single = False

        if isinstance(models, ASTNode):
            single = True
            models = [models]

        for model in models:
            model.accept(self.SiftRewriterVisitor())

        if single:
            return models[0]

        return models
