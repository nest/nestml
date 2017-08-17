"""
@author kperun
TODO header
"""
from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
from pynestml.src.main.python.org.nestml.ast.ASTVariable import ASTVariable


class ASTSimpleExpression:
    """
    This class is used to store a simple expression, e.g. +42mV.
    ASTSimpleExpression, consisting of a single element without combining operator, e.g.,10mV, inf, V_m.
    Grammar:
    simpleExpression : functionCall
                       | BOOLEAN_LITERAL // true & false
                       | NUMERIC_LITERAL (variable)?
                       | NAME
                       | 'inf'
                       | variable;
    """
    __functionCall = None
    __name = None
    __numericLiteral = None
    __variable = None
    __isBooleanTrue = False
    __isBooleanFalse = False
    __isInf = False

    def __init__(self, _functionCall=None, _name=None, _booleanLiteral=None, _numericLiteral=None, _isInf=False,
                 _variable=None):
        """
        Standard constructor.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _name: a string, e.g., a certain index.
        :type _name: str
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: str
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        """
        self.__functionCall = _functionCall
        self.__name = _name
        if _booleanLiteral is not None:
            if _booleanLiteral is 'True' or _booleanLiteral is 'true':
                self.__isBooleanTrue = True
            else:
                self.__isBooleanFalse = True
        self.__numericLiteral = _numericLiteral
        self.__isInf = _isInf
        self.__variable = _variable

    @classmethod
    def makeASTSimpleExpression(cls, _functionCall=None, _name=None, _booleanLiteral=None, _numericLiteral=None,
                                _isInf=False, _variable=None):
        """
        The factory method of the ASTSimpleExpression class.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _name: a string, e.g., a certain index.
        :type _name: str
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: str
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :return: a new ASTSimpleExpression object.
        :rtype: ASTSimpleExpression
        """
        assert (_functionCall is None or isinstance(_functionCall,
                                                    ASTFunctionCall)), '(PyNESTML.AST) Not a function call provided.'
        assert (_name is None or isinstance(_name, str)), '(PyNESTML.AST) Not a string provided as name.'
        assert (_booleanLiteral is None or isinstance(_booleanLiteral, bool)), '(PyNESTML.AST) Not a bool provided.'
        assert (_isInf is None or isinstance(_isInf, bool)), '(PyNESTML.AST) Not a bool provided.'
        assert (_variable is None or isinstance(_variable, ASTVariable)), '(PyNESTML.AST) Not a variable provided.'
        return cls(_functionCall, _name, _booleanLiteral, _numericLiteral, _isInf, _variable)

    def isFunctionCall(self):
        """
        Returns whether it is a function call or not.
        :return: True if function call, otherwise False.
        :rtype: bool
        """
        return self.__functionCall is not None

    def getFunctionCall(self):
        """
        Returns the function call object.
        :return: the function call object.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def isBooleanTrue(self):
        """
        Returns whether it is a boolean true literal.
        :return: True if true literal, otherwise False.
        :rtype: bool 
        """
        return self.__isBooleanTrue

    def isBooleanFalse(self):
        """
        Returns whether it is a boolean false literal.
        :return: True if false literal, otherwise False.
        :rtype: bool
        """
        return self.__isBooleanFalse

    def isNumericLiteral(self):
        """
        Returns whether it is a numeric literal or not.
        :return: True if numeric literal, otherwise False.
        :rtype: bool
        """
        return self.__numericLiteral is not None

    def getNumericLiteral(self):
        """
        Returns the value of the numeric literal.
        :return: the value of the numeric literal.
        :rtype: int/float
        """
        return self.__numericLiteral

    def isInfLiteral(self):
        """
        Returns whether it is a infinity literal or not.
        :return: True if infinity literal, otherwise False.
        :rtype: bool
        """
        return self.__isInf

    def isVariable(self):
        """
        Returns whether it is a variable or not.
        :return: True if has a variable, otherwise False.
        :rtype: bool
        """
        return self.__variable is not None

    def getVariable(self):
        """
        Returns the variable.
        :return: the variable object.
        :rtype: ASTVariable
        """
        return self.__variable

    def isName(self):
        """
        Returns whether it is a simple name or not.
        :return: True if has a simple name, otherwise False.
        :rtype: bool
        """
        return self.__name is not None

    def getName(self):
        """
        Returns the name.
        :return: the name.
        :rtype: str
        """
        return self.__name

    def printAST(self):
        """
        Returns the string representation of the simple expression.
        :return: the operator as a string.
        :rtype: str
        """
        if self.isFunctionCall():
            return self.__functionCall.printAST()
        elif self.isBooleanTrue():
            return 'True'
        elif self.isBooleanFalse():
            return 'False'
        elif self.isInfLiteral():
            return 'inf'
        elif self.isName():
            return self.__name
        elif self.isNumericLiteral():
            if self.isVariable():
                return str(self.__numericLiteral) + self.__variable.printAST()
            else:
                return str(self.__numericLiteral)
        elif self.isVariable():
            return self.__variable.printAST()
        else:
            raise Exception("(NESTML) Simple expression not specified.")
