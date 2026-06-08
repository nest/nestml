# -*- coding: utf-8 -*-
#
# equations_with_delay_vars_transformer.py
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

from typing import Any, Dict, Iterable, Mapping, Optional, Set, Tuple

import odetoolbox

from pynestml.visitors.ast_equations_with_delay_vars_visitor import ASTEquationsWithDelayVarsVisitor

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.meta_model.ast_model import ASTModel
from pynestml.transformers.transformer import Transformer


class EquationsWithDelayVarsTransformer(Transformer):
    r"""
    Convert the delay variables parsed as function calls to ASTVariable and collects all the equations that have these delay variables in the metadata with key ``equations_with_delay_vars``.

    Warning: this transformer sets attributes on the symbols in the model symbol table. If the ASTSymbolTableVisitor is run on the model, these attributes are lost.
    """

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        for model in models:
            equations_with_delay_vars_visitor = ASTEquationsWithDelayVarsVisitor()
            model.accept(equations_with_delay_vars_visitor)

            if not model.name in metadata.keys():
                metadata[model.name] = {}

            metadata[model.name]["equations_with_delay_vars"] = equations_with_delay_vars_visitor.equations

        return models
