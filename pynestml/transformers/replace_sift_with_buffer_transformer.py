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

from typing import Callable, Dict, Iterable, List, Optional, Mapping, Any, Union, Sequence

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

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
                parent.function_call = None
                parent.variable = node.args[0].variable
                parent.variable.parent = parent
                parent.implicit_conversion_factor = node.args[0].get_implicit_conversion_factor()

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:

        for model in models:
            model.accept(self.SiftRewriterVisitor())

        return models
