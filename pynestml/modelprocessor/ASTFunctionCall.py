#
# ASTFunctionCall.py
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


from pynestml.modelprocessor.ASTNode import ASTElement


class ASTFunctionCall(ASTElement):
    """
    This class is used to store a single function call.
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the function
    @attribute args Comma separated list of expressions representing parameters.
    Grammar:
        functionCall : calleeName=NAME '(' (expression (',' expression)*)? ')';
    """
    __calleeName = None
    __args = None

    def __init__(self, _calleeName=None, _args=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _calleeName: the name of the function which is called.
        :type _calleeName: str
        :param _args: (Optional) List of arguments
        :type _args: list(ASTExpression)
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        from pynestml.modelprocessor.ASTExpression import ASTExpression
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        assert (_calleeName is not None and isinstance(_calleeName, str)), \
            '(PyNestML.AST.FunctionCall) No or wrong type of name of the called function provided (%s)!' % type(
                _calleeName)
        assert (_args is None or isinstance(_args, list)), \
            '(PyNestML.AST.FunctionCall) No or wrong type of arguments provided (%s)!' % type(_args)
        for arg in _args:
            assert (arg is not None and (isinstance(arg, ASTExpression) or
                                         isinstance(arg, ASTSimpleExpression))), \
                '(PyNestML.AST.FunctionCall) No or wrong type of argument provided (%s)' % type(arg)
        super(ASTFunctionCall, self).__init__(_sourcePosition)
        self.__calleeName = _calleeName
        self.__args = _args
        return

    @classmethod
    def makeASTFunctionCall(cls, _calleeName=None, _args=None, _sourcePosition=None):
        """
        Factory method of the ASTFunctionCall class.
        :param _calleeName: the name of the function which is called.
        :type _calleeName: str
        :param _args: (Optional) List of arguments
        :type _args: list(ASTExpression)
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTFunctionCall object.
        :rtype: ASTFunctionCall
        """
        return cls(_calleeName, _args, _sourcePosition)

    def getName(self):
        """
        Returns the name of the called function.
        :return: the name of the function.
        :rtype: str.
        """
        return self.__calleeName

    def hasArgs(self):
        """
        Returns whether function call has arguments or not.
        :return: True if has arguments, otherwise False.
        :rtype: bool
        """
        return (self.__args is not None) and len(self.__args) > 0

    def getArgs(self):
        """
        Returns the list of arguments.
        :return: the list of arguments.
        :rtype: list(ASTExpression)
        """
        return self.__args

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for param in self.getArgs():
            if param is _ast:
                return self
            elif param.getParent(_ast) is not None:
                return param.getParent(_ast)
        return None

    def __str__(self):
        """
        Returns the string representation of the function call.
        :return: the function call as a string.
        :rtype: str
        """
        ret = str(self.__calleeName) + '('
        for i in range(0, len(self.__args)):
            ret += str(self.__args[i])
            if i < len(self.__args) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += ')'
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTFunctionCall):
            return False
        if self.getName() != _other.getName():
            return False
        if len(self.getArgs()) != len(_other.getArgs()):
            return False
        myArgs = self.getArgs()
        yourArgs = _other.getArgs()
        for i in range(0, len(myArgs)):
            if not myArgs[i].equals(yourArgs[i]):
                return False
        return True
