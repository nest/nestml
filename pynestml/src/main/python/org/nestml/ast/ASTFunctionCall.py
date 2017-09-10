"""
/*
 *  ASTFunctionCall.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTFunctionCall(ASTElement):
    """
    This class is used to store a single function call.
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the function
    @attribute args Comma separated list of expressions representing parameters.
    Grammar:
        functionCall : calleeName=NAME '(' (args=arguments)? ')';
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
        assert (_calleeName is not None),\
            '(PyNestML.AST.FunctionCall) Name of called function not provided!'
        assert (_args is None or isinstance(_args, list)), \
            '(PyNestML.AST.FunctionCall) Arguments must be list of expressions!'
        super(ASTFunctionCall, self).__init__(_sourcePosition)
        self.__calleeName = _calleeName
        self.__args = _args

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

    def printAST(self):
        """
        Returns the string representation of the function call.
        :return: the function call as a string.
        :rtype: str
        """
        ret = str(self.__calleeName) + '('
        for i in range(0, len(self.__args)):
            ret += self.__args[i].printAST()
            if i < len(self.__args) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += ')'
        return ret
