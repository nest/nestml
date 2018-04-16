#
# OdeTransformer.py
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

from pynestml.meta_model.ASTFunctionCall import ASTFunctionCall
from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.visitors.ASTHigherOrderVisitor import ASTHigherOrderVisitor


class OdeTransformer(object):
    """
    This class contains several methods as used to transform ODEs.
    """
    functions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE,
                 PredefinedFunctions.BOUNDED_MAX, PredefinedFunctions.BOUNDED_MIN)
    sum_functions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE)

    @classmethod
    def replace_functions(cls, _ast):
        """
        Replaces all self.function in the handed over node.
        :param _ast: a single meta_model node.
        :type _ast: AST_
        """
        working_copy = copy(_ast)
        function_calls = cls.get_function_calls(working_copy, cls.functions)
        for call in function_calls:
            cls.replace_function_call_through_first_argument(working_copy, call)
        return working_copy

    @classmethod
    def replace_sum_calls(cls, ast):
        """
        Replaces all sum calls in the handed over node.
        :param ast: a single node
        :type ast: AST_
        """
        working_copy = copy(ast)
        function_calls = cls.get_sum_function_calls(working_copy)
        for call in function_calls:
            cls.replace_function_call_through_first_argument(working_copy, call)
        return ast

    @classmethod
    def replace_function_call_through_first_argument(cls, ast, to_replace):
        """
        Replaces all occurrences of the handed over function call by the first argument.
        :param ast: a single meta_model node
        :type ast: AST_
        :param to_replace: the function to replace
        :type to_replace: ASTFunctionCall
        """

        # we define a local collection operation
        def replace_function_call_through_first_argument(node):
            if isinstance(node,
                          ASTSimpleExpression) and node.is_function_call() and node.get_function_call() == to_replace:
                first_arg = node.get_function_call().get_args()[0].get_variable()
                node.set_function_call(None)
                node.set_variable(first_arg)
            return

        ast.accept(ASTHigherOrderVisitor(replace_function_call_through_first_argument))
        return

    @classmethod
    def get_sum_function_calls(cls, ast):
        """
        Returns all sum function calls in the handed over meta_model node or one of its children.
        :param ast: a single meta_model node.
        :type ast: AST_
        """
        return cls.get_function_calls(ast, cls.sum_functions)

    @classmethod
    def contains_sum_function_call(cls, ast):
        """
        Indicates whether _ast or one of its child nodes contains a sum call.
        :param ast: a single meta_model
        :type ast: AST_
        :return: True if sum is contained, otherwise False.
        :rtype: bool
        """
        return len(cls.get_function_calls(ast, cls.sum_functions)) > 0

    @classmethod
    def get_function_calls(cls, ast_node, function_list):
        """
        For a handed over list of function names, this method retrieves all functions in the meta_model.
        :param ast_node: a single meta_model node
        :type ast_node: AST_
        :param function_list: a list of function names
        :type function_list: list(str)
        :return: a list of all functions in the meta_model
        :rtype: list(ASTFunctionCall)
        """
        res = list()

        def loc_get_function(node):
            if isinstance(node, ASTFunctionCall) and node.get_name() in function_list:
                res.append(node)

        ast_node.accept(ASTHigherOrderVisitor(loc_get_function, list()))
        return res

    @classmethod
    def get_cond_sum_function_call(cls, node):
        """
        Collects all cond_sum function calls in the meta_model.
        :param node: a single meta_model node
        :type node: AST_
        :return: a list of all functions in the meta_model
        :rtype: list(ASTFunctionCall)
        """
        res = list()

        def loc_get_cond_sum(a_node):
            if isinstance(a_node, ASTFunctionCall) and a_node.get_name() == PredefinedFunctions.COND_SUM:
                res.append(a_node)

        node.accept(ASTHigherOrderVisitor(loc_get_cond_sum))
        return res
