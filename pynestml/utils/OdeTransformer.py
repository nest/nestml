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
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression

from copy import copy


class OdeTransformer(object):
    """
    This class contains several methods as used to transform ODEs.
    """
    __functions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE,
                   PredefinedFunctions.BOUNDED_MAX, PredefinedFunctions.BOUNDED_MIN)
    __sumFunctions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE)

    @classmethod
    def replaceFunctions(cls, _ast):
        """
        Replaces all self.function in the handed over node.
        :param _ast: a single ast node.
        :type _ast: AST_
        """
        workingCopy = copy(_ast)
        functionCalls = cls.getFunctionCalls(workingCopy, cls.__functions)
        for call in functionCalls:
            cls.replaceFunctionCallThroughFirstArgument(workingCopy, call)
        return workingCopy

    @classmethod
    def replaceSumCalls(cls, _ast):
        """
        Replaces all sum calls in the handed over node.
        :param _ast: a single node
        :type _ast: AST_
        """
        assert (_ast is not None), '(PyNestML.Utils) No ast provided!'
        workingCopy = copy(_ast)
        functionCalls = cls.get_sumFunctionCalls(workingCopy)
        for call in functionCalls:
            cls.replaceFunctionCallThroughFirstArgument(workingCopy, call)
        return _ast

    @classmethod
    def replaceFunctionCallThroughFirstArgument(cls, _ast=None, _toReplace=None):
        """
        Replaces all occurrences of the handed over function call by the first argument.
        :param _ast: a single ast node
        :type _ast: AST_
        :param _toReplace: the function to replace
        :type _toReplace: ASTFunctionCall
        """

        # we define a local collection operation
        def replace_function_call_through_first_argument(node):
            if isinstance(node, ASTSimpleExpression) and node.is_function_call() and node.get_function_call() == _toReplace:
                first_arg = node.get_function_call().get_args()[0].get_variable()
                node.set_function_call(None)
                node.set_variable(first_arg)
            return

        _ast.accept(ASTHigherOrderVisitor(replace_function_call_through_first_argument))
        return

    @classmethod
    def get_sumFunctionCalls(cls, _ast=None):
        """
        Returns all sum function calls in the handed over ast node or one of its children.
        :param _ast: a single ast node.
        :type _ast: AST_
        """
        return cls.getFunctionCalls(_ast, cls.__sumFunctions)

    @classmethod
    def containsSumFunctionCall(cls, _ast):
        """
        Indicates whether _ast or one of its child nodes contains a sum call.
        :param _ast: a single ast
        :type _ast: AST_
        :return: True if sum is contained, otherwise False.
        :rtype: bool
        """
        return len(cls.getFunctionCalls(_ast, cls.__sumFunctions)) > 0

    @classmethod
    def getFunctionCalls(cls, _astNode=None, _functionList=list()):
        """
        For a handed over list of function names, this method retrieves all functions in the ast.
        :param _astNode: a single ast node
        :type _astNode: AST_
        :param _functionList: a list of function names
        :type _functionList: list(str)
        :return: a list of all functions in the ast
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall

        def loc_get_function(node):
            if isinstance(node, ASTFunctionCall) and node.get_name() in _functionList:
                res.append(node)

        _astNode.accept(ASTHigherOrderVisitor(loc_get_function, list()))
        return res

    @classmethod
    def getCondSumFunctionCall(cls, node):
        """
        Collects all cond_sum function calls in the ast.
        :param node: a single ast node
        :type node: AST_
        :return: a list of all functions in the ast
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall

        def loc_get_cond_sum(node):
            if isinstance(node, ASTFunctionCall) and node.get_name() == PredefinedFunctions.COND_SUM:
                res.append(node)

        node.accept(ASTHigherOrderVisitor(loc_get_cond_sum))

        return res
