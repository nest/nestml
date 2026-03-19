# -*- coding: utf-8 -*-
#
# transformer.py
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

from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.with_options import WithOptions

from abc import ABCMeta, abstractmethod


class Transformer(WithOptions, metaclass=ABCMeta):
    r"""Perform a transformation step on models, for instance, rewriting disallowed variable names like "lambda" because they conflict with keywords in the target language.

    Transformers operate on sets of models and produce sets of models (possibly of unequal size). For instance, some transformers accept a pair consisting of neuron and synapse, processing these together to create a new, interlinked model.

    Additionally, as a side effect, transformers may produce metadata about models, that contains information that can be helpful for subsequent transformers as well as code generation (for instance, the results of ODE-toolbox, detailing the numerical solver that is to be used for a model). The ``metadata`` dictionary is a mapping from the name of the model (as a string) to a dictionary of key/value pairs that contain the metadata (of arbitrary type, indexed by strings as keys) for that model."""

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    @abstractmethod
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Union[ASTModel, Iterable[ASTModel]]:
        raise NotImplementedError()
