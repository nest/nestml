# -*- coding: utf-8 -*-
#
# equations_with_vector_vars_transformer.py
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

from typing import Any, Dict, Iterable

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.meta_model.ast_model import ASTModel
from pynestml.transformers.transformer import Transformer
from pynestml.visitors.ast_equations_with_vector_variables import ASTEquationsWithVectorVariablesVisitor


class EquationsWithVectorVarsTransformer(Transformer):
    r"""
    """

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        for model in models:
            # Collect all the equations with vector variables
            eqns_with_vector_vars_visitor = ASTEquationsWithVectorVariablesVisitor()
            model.accept(eqns_with_vector_vars_visitor)

            if not model.name in metadata.keys():
                metadata[model.name] = {}

            metadata[model.name]["equations_with_vector_vars"] = eqns_with_vector_vars_visitor.equations

        return models
