# -*- coding: utf-8 -*-
#
# ast_expression_node.py
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
from abc import ABCMeta
from copy import copy

from pynestml.meta_model.ast_node import ASTNode


class ASTExpressionNode(ASTNode):
    """
    This class is not a part of the grammar but is used to store commonalities of expression-type nodes.

    This class is abstract, thus no instances can be created.
    """
    __type = None
    __typeEither = None
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        super(ASTExpressionNode, self).__init__(*args, **kwargs)

    @property
    def type(self):
        from pynestml.visitors.ast_expression_type_visitor import ASTExpressionTypeVisitor
        if self.__type is None:
            self.accept(ASTExpressionTypeVisitor())
        return copy(self.__type)

    @type.setter
    def type(self, _value):
        self.__type = _value

    def get_parent(self, ast):
        pass

    def equals(self, other):
        pass
