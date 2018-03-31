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
from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from copy import copy, deepcopy


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
            cls.replace_function_call_through_first_argument(workingCopy, call)
        return workingCopy

    @classmethod
    def refactor_convolve_call(cls, _ast):
        """
        Replaces all `convolve` calls in the handed over node.
        :param _ast: a single node
        :type _ast: AST_
        """

        function_calls = cls.get_sumFunctionCalls(_ast)
        for call in function_calls:
            cls.replace_function_call_through_first_argument(_ast, call)

    @classmethod
    def replace_function_call_through_first_argument(cls, ast, function_name_to_replace):
        """
        Replaces all occurrences of the handed over function call by the first argument.
        :param ast: a single ast node
        :type ast: AST_
        :param function_name_to_replace: the function to replace
        :type function_name_to_replace: ASTFunctionCall
        """

        # we define a local collection operation
        def replace_function_call_through_first_argument(_expr=None):
            if _expr.isFunctionCall() and _expr.getFunctionCall() == function_name_to_replace:
                firstArg = _expr.getFunctionCall().getArgs()[0].getVariable()
                _expr.setFunctionCall(None)
                _expr.setVariable(firstArg)
            return

        ASTHigherOrderVisitor.visit(ast,
                                    lambda x: replace_function_call_through_first_argument(x) if isinstance(x, ASTSimpleExpression) else True)

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
        ASTHigherOrderVisitor.visit(_astNode,
                                    lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and x.getName() in _functionList else True)
        return res

    @classmethod
    def getCondSumFunctionCalls(cls, _astNode=None):
        """
        Collects all cond_sum function calls in the ast.
        :param _astNode: a single ast node
        :type _astNode: AST_
        :return: a list of all functions in the ast
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        ASTHigherOrderVisitor.visit(_astNode, lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and
                                                                         x.getName() == PredefinedFunctions.COND_SUM
        else True)
        return res
