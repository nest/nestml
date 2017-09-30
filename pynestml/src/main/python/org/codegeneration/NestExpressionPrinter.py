#
# NestExpressionPrinter.py
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

class NestExpressionPrinter(object):
    """
    This class contains all methods as required to transform
    """

    @classmethod
    def printExpression(cls, _ast):
        """
        Prints the handed over expression to a nest readable format.
        :param _ast: a single ast node.
        :type _ast: ASTExpression or ASTSimpleExpression
        :return: the corresponding string representation
        :rtype: str
        """
        return "TODO expr"

    @classmethod
    def printMethodCall(cls,_ast):
        """
        Prints a single handed over function call.
        :param _ast: a single function call.
        :type _ast: ASTFunctionCall
        :return: the corresponding string representation.
        :rtype: str
        """
        return "TODO function"