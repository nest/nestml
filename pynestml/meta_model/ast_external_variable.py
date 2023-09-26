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

from pynestml.meta_model.ast_variable import ASTVariable


class ASTExternalVariable(ASTVariable):
    r"""
    This class is used to store a single "external" variable: a variable the value of which is obtained during runtime from a neuron's postsynaptic partner.
    """
    _altscope = None
    _altname = None

    def __init__(self, name, altname=None, altscope=None, *args, **kwargs):
        r"""
        Standard constructor.
        """
        super(ASTExternalVariable, self).__init__(name, *args, **kwargs)
        self._altname = altname
        self._altscope = altscope

    def clone(self):
        r"""
        Return a clone ("deep copy") of this node.
        """
        return ASTExternalVariable(altname=self._altname,
                                   altscope=self._altscope,
                                   # ASTVariable attributes:
                                   name=self.name,
                                   differential_order=self.differential_order,
                                   type_symbol=self.type_symbol,
                                   vector_parameter=self.vector_parameter,
                                   # ASTNode common attributes:
                                   source_position=self.get_source_position(),
                                   scope=self.scope,
                                   comment=self.comment,
                                   pre_comments=[s for s in self.pre_comments],
                                   in_comment=self.in_comment,
                                   implicit_conversion_factor=self.implicit_conversion_factor)

    def update_alt_scope(self, scope):
        self._altscope = scope

    def set_alternate_name(self, alternate_name: Optional[str]):
        self._altname = alternate_name

    def get_alternate_name(self):
        return self._altname

    def get_scope(self):
        if self._altscope:
            return self._altscope.get_scope()
        return self.scope
