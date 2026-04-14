# -*- coding: utf-8 -*-
#
# convolutions_to_buffers_transformer.py
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

from typing import Any, Dict, Iterable, List, Optional, Mapping, Sequence

from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.ast_utils import ASTUtils

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

import re

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.transformers.transformer import Transformer
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor


class ConvolutionsToBuffersTransformer(Transformer):
    r"""
    Replace all occurrences of `convolve(kernel[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a kernel named `g_E` and a spike input port named `spikes_exc`.

    Store metadata pertaining to which buffer variables are needed (with key ``kernel_buffers``) and metadata pertaining to increments due to delta kernels (with key ``delta_factors``).
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        for model in models:
            if not model.get_equations_blocks():
                continue

            if len(model.get_equations_blocks()) > 1:
                raise Exception("Only one equations block per model supported for now")

            equations_block = model.get_equations_blocks()[0]

            if not model.name in metadata.keys():
                metadata[model.name] = {}

            metadata[model.name]["kernel_buffers"] = ASTUtils.generate_kernel_buffers(model, equations_block)
            metadata[model.name]["delta_factors"] = ASTUtils.get_delta_factors_(model, equations_block)
            ASTUtils.replace_convolve_calls_with_buffers_(model, equations_block)

        return models
