# -*- coding: utf-8 -*-
#
# ast_function_call.py
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

from pynestml.meta_model.ast_node import ASTNode


class ASTFunctionCall(ASTNode):
    """
    This class is used to store a single function call.
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the function
    @attribute args Comma separated list of expressions representing parameters.
    Grammar:
        functionCall : calleeName=NAME '(' (rhs (',' rhs)*)? ')';
    Attributes:
        callee_name = None
        args = None
    """

    def __init__(self, callee_name, function_call_args, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param callee_name: the name of the function which is called.
        :type callee_name: str
        :param function_call_args: (Optional) List of arguments
        :type function_call_args: List[ASTExpression]
        """
        super(ASTFunctionCall, self).__init__(*args, **kwargs)
        assert type(callee_name) is str
        self.callee_name = callee_name
        self.args = function_call_args

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTFunctionCall
        """
        function_call_args_dup = None
        if self.args is not None:
            function_call_args_dup = [function_call_arg.clone() for function_call_arg in self.args]
        dup = ASTFunctionCall(callee_name=self.callee_name,
                              function_call_args=function_call_args_dup,
                              # ASTNode common attributes:
                              source_position=self.source_position,
                              scope=self.scope,
                              comment=self.comment,
                              pre_comments=[s for s in self.pre_comments],
                              in_comment=self.in_comment,
                              post_comments=[s for s in self.post_comments],
                              implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_name(self):
        """
        Returns the name of the called function.
        :return: the name of the function.
        :rtype: str.
        """
        return self.callee_name

    def has_args(self):
        """
        Returns whether function call has arguments or not.
        :return: True if has arguments, otherwise False.
        :rtype: bool
        """
        return (self.args is not None) and len(self.args) > 0

    def get_args(self):
        """
        Returns the list of arguments.
        :return: the list of arguments.
        :rtype: list(ASTExpression)
        """
        return self.args

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for param in self.get_args():
            if param is ast:
                return self
            if param.get_parent(ast) is not None:
                return param.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTFunctionCall):
            return False
        if self.get_name() != other.get_name():
            return False
        if len(self.get_args()) != len(other.get_args()):
            return False
        my_args = self.get_args()
        your_args = other.get_args()
        for i in range(0, len(my_args)):
            if not my_args[i].equals(your_args[i]):
                return False
        return True
