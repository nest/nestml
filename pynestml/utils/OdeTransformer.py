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
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from copy import copy


class OdeTransformer(object):
    """
    This class contains several methods as used to transform ODEs.
    """

    def replaceSumCalls(self, _expression=None):
        """
        For a handed over expression, this method replaces all occurrences of the convolve,cond_sum or curr_sum
        by the respective first parameter.
        :param _expression: a single expression.
        :type _expression: ASTExpression or ASTSimpleExpression
        :return: a new expression which does not contain those sums
        :rtype: ASTExpression/ASTSimpleExpression
        """
        # todo
        return _expression
        from pynestml.nestml.ASTExpression import ASTExpression
        from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
        if isinstance(_expression, ASTSimpleExpression) and _expression.isFunctionCall():
            call = _expression.getFunctionCall()
            if call.getName() == PredefinedFunctions.CONVOLVE or call.getName() == PredefinedFunctions.COND_SUM or \
                            call.getName() == PredefinedFunctions.CURR_SUM:
                # we can be sure that it is a variable, since it is ensured by a coco
                variable = _expression.getFunctionCall().getArgs()[0]
                # so in the end, we replace a function call by a variable
                newExpr = ASTSimpleExpression.makeASTSimpleExpression(_variable=variable)
                newExpr.updateScope(_expression.getScope())
                return newExpr
        elif isinstance(_expression, ASTExpression):
            copyExpr = copy(_expression)
            return
