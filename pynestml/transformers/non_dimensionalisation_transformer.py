# -*- coding: utf-8 -*-
#
# non_dimensionalisation_transformer.py
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

from typing import Any, Sequence, Mapping, Optional, Union

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class NonDimensionalisationTransformer(Transformer):
    r"""Remove all units from the model and replace them with real type.

    NESTML model:
        V_m V = -70 mV

    generated code:
        float V_m = -0.07   # implicit: units of V
        float V_m = -70   # implicit: units of mV


    """

    # _default_options = {
    #     "quantity_to_preferred_prefix": {
    #         "time": "m",
    #         "voltage": "m"
    #     },
    #     "variable_to_preferred_prefix": {
    #         "V_m": "m",
    #         "V_dend": "u"
    #     }
    # }

    _default_options = {
        "quantity_to_preferred_prefix": {
        },
        "variable_to_preferred_prefix": {
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def transform_(self, model: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        transformed_model = model.duplicate()

        for quantity, preferred_prefix in self.get_option("quantity_to_preferred_prefix").items():
            pass

        return transformed_model

    def transform(self, models: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        transformed_models = []

        single = False
        if isinstance(models, ASTNode):
            single = True
            model = [models.duplicate()]

        for model in models:
            transformed_models.append(self.transform_(model))

        if single:
            return transformed_models[0]

        return transformed_models
