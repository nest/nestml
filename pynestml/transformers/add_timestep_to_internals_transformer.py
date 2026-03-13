# -*- coding: utf-8 -*-
#
# add_timestep_to_internals_transformer.py
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

from typing import Any, Iterable, Mapping, Optional, Union

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.transformers.transformer import Transformer


class AddTimestepToInternalsTransformer(Transformer):
    r"""
    Add timestep variable to the internals block
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Union[ASTModel, Iterable[ASTModel]]:

        for model in models:
            self.add_timestep_symbol(model)

        return models

    @classmethod
    def add_timestep_symbol(cls, model: ASTModel) -> None:
        r"""
        Add timestep variable to the internals block
        """
        from pynestml.utils.model_parser import ModelParser
        assert model.get_initial_value("__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in model.get_internal_symbols()], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        model.add_to_internals_block(ModelParser.parse_declaration("__h ms = resolution()"), index=0)
