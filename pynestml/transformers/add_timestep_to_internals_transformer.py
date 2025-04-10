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

from typing import Optional, Mapping, Any, Union, Sequence
from pynestml.meta_model.ast_model import ASTModel

from pynestml.meta_model.ast_node import ASTNode
from pynestml.transformers.transformer import Transformer


class AddTimestepToInternalsTransformer(Transformer):
    r"""
    Add timestep variable to the internals block
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        single = False
        if isinstance(models, ASTNode):
            single = True
            models = [models]

        for model in models:
            self.add_timestep_symbol(model)

        if single:
            return models[0]

        return models

    @classmethod
    def add_timestep_symbol(cls, model: ASTModel) -> None:
        r"""
        Add timestep variable to the internals block
        """
        from pynestml.utils.model_parser import ModelParser
        assert model.get_initial_value(
            "__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in model.get_internal_symbols(
        )], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        model.add_to_internals_block(ModelParser.parse_declaration('__h ms = resolution()'), index=0)
