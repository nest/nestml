# -*- coding: utf-8 -*-
#
# cloning_helpers.py
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
import numpy as np
from pynestml.meta_model.ast_node import ASTNode


def clone_numeric_literal(numeric_literal):
    if numeric_literal is None:
        return None

    if type(numeric_literal) in [int, float]:
        # Python basic type
        return numeric_literal

    if type(numeric_literal) in [np.int, np.int8, np.int16, np.int32, np.int64]:
        # NumPy types
        return numeric_literal.copy()

    if isinstance(numeric_literal, ASTNode):
        return numeric_literal.clone()

    assert False, "Asked to copy unknown numeric literal (type: " + \
        str(type(numeric_literal)) + " ): " + str(numeric_literal)
