# -*- coding: utf-8 -*-
#
# ast_external_variable.py
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
from typing import Optional

from copy import copy

from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.either import Either


class ASTExternalVariable(ASTVariable):
    """
    This class is used to store a single "external" variable: a variable the value of which is obtained during runtime from a neuron's postsynaptic partner.

    Grammar:
        variable : NAME (differentialOrder='\'')*;
    Attributes:
        name = None
        differential_order = None
        # the corresponding type symbol
        type_symbol = None
    """
    _altscope = None
    _altname = None
    
    # XXX: TODO: CLONE METHOD

    def update_scope2(self, scope):
        self._altscope = scope

    def set_alternate_name(self, alternate_name: Optional[str]):
        self._altname = alternate_name

    def get_alternate_name(self):
        return self._altname

    def get_scope(self):
        if self._altscope:
            return self._altscope
        return self.scope
