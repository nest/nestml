# -*- coding: utf-8 -*-
#
# ode_transformer.py
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
from copy import copy

from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor


class OdeTransformer(object):
    """
    This class contains several methods as used to transform ODEs.
    """

    @classmethod
    def get_convolve_function_calls(cls, ast):
        """
        Returns all sum function calls in the handed over meta_model node or one of its children.
        :param ast: a single meta_model node.
        :type ast: ASTNode
        """
        return cls.get_function_calls(ast, PredefinedFunctions.CONVOLVE)

    @classmethod
    def contains_convolve_function_call(cls, ast):
        """
        Indicates whether _ast or one of its child nodes contains a sum call.
        :param ast: a single meta_model
        :type ast: ASTNode
        :return: True if sum is contained, otherwise False.
        :rtype: bool
        """
        return len(cls.get_function_calls(ast, PredefinedFunctions.CONVOLVE)) > 0

    @classmethod
    def get_function_calls(cls, ast_node, function_list):
        """
        For a handed over list of function names, this method retrieves all functions in the meta_model.
        :param ast_node: a single meta_model node
        :type ast_node: ASTNode
        :param function_list: a list of function names
        :type function_list: list(str)
        :return: a list of all functions in the meta_model
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        from pynestml.meta_model.ast_function_call import ASTFunctionCall
        fun = (lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and x.get_name() in function_list else True)
        vis = ASTHigherOrderVisitor(visit_funcs=fun)
        ast_node.accept(vis)
        return res
