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

from typing import Any, List, Mapping, Optional, Sequence

from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.with_options import WithOptions

from abc import ABCMeta, abstractmethod
import copy


class Transformer(WithOptions, metaclass=ABCMeta):
    r"""Perform a model transformation step, for instance, rewriting disallowed variable names like "lambda" because it conflicts with a keyword."""

    def __init__(self, options: Optional[Mapping[str, Any]]=None):
        super(Transformer, self).__init__(options)

    @abstractmethod
    def transform(self, model: ASTNode) -> ASTNode:
        pass
