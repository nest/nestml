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

from typing import Any, Mapping, Optional, Union, Sequence

from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.with_options import WithOptions

from abc import ABCMeta, abstractmethod


class Transformer(WithOptions, metaclass=ABCMeta):
    r"""Perform a transformation step on models, for instance, rewriting disallowed variable names like "lambda" because it conflicts with a keyword.

    Some transformers operate on individual models, and some operate on tuples of models (for instance, a pair (neuron, synapse))."""

    def __init__(self, options: Optional[Mapping[str, Any]]=None):
        super(Transformer, self).__init__(options)

    @abstractmethod
    def transform(self, model: Union[ASTNode, Sequence[ASTNode]]) -> Union[ASTNode, Sequence[ASTNode]]:
        assert False
