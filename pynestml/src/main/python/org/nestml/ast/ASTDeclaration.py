"""
@author kperun
TODO header
"""


class ASTDeclaration:
    """
    This class is used to store declarations.
    ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
    'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute hide is true iff. declaration is not traceable.
    @attribute function is true iff. declaration is an function.
    @attribute vars          List with variables
    @attribute Datatype      Obligatory data type, e.g. 'real' or 'mV/s'
    @attribute sizeParameter An optional array parameter. E.g. 'tau_syn ms[n_receptors]'
    @attribute expr An optional initial expression, e.g. 'a real = 10+10'
    @attribute invariants List with optional invariants.
    Grammar:
        declaration :
            ('recordable')? ('function')?
            variable (',' variable)*
            datatype
            ('[' sizeParameter=NAME ']')?
            ( '=' expression)? SL_COMMENT?
            ('[[' invariant=expression ']]')?;
    """
    __isRecordable = False
    __isFunction = False
    __variables = None
    __dataType = None
    __sizeParameter = None
    __expression = None
    __comment = None
    __invariant = None

    def __init__(self, _isRecordable=False, _isFunction=False, _variables=list(), _dataType=None,
                 _sizeParameter=None, _expression=None, _comment=None, _invariant=None):
        """
        Standard constructor.
        :param _isRecordable: is a recordable declaration.
        :type _isRecordable: bool
        :param _isFunction: is a function declaration.
        :type _isFunction: bool
        :param _variables: a list of variables.
        :type _variables: list(ASTVariable)
        :param _dataType: the data type.
        :type _dataType: ASTDataType
        :param _sizeParameter: an optional size parameter.
        :type _sizeParameter: str
        :param _expression: an optional right-hand side expression.
        :type _expression: ASTExpression
        :param _comment: an optional comment.
        :type _comment: str
        :param _invariant: a optional invariant.
        :type _invariant: ASTExpression.
        """
        self.__isRecordable = _isRecordable
        self.__isFunction = _isFunction
        self.__variables = _variables
        self.__dataType = _dataType
        self.__sizeParameter = _sizeParameter
        self.__expression = _expression
        self.__comment = _comment
        self.__invariant = _invariant

    @classmethod
    def makeASTDeclaration(cls, _isRecordable=False, _isFunction: bool = False, _variables=list(), _dataType=None,
                           _sizeParameter=None, _expression=None, _comment=None, _invariant=None):
        """
        The factory method of the ASTDeclaration class.
        :param _isRecordable: is a recordable declaration.
        :type _isRecordable: bool
        :param _isFunction: is a function declaration.
        :type _isFunction: bool
        :param _variables: a list of variables.
        :type _variables: list(ASTVariable)
        :param _dataType: the data type.
        :type _dataType: ASTDataType
        :param _sizeParameter: an optional size parameter.
        :type _sizeParameter: str
        :param _expression: an optional right-hand side expression.
        :type _expression: ASTExpr
        :param _comment: an optional comment.
        :type _comment: str
        :param _invariant: a optional invariant.
        :type _invariant: ASTExpr.
        :return: a new ASTDeclaration object.
        :rtype: ASTDeclaration
        """
        return cls(_isRecordable, _isFunction, _variables, _dataType, _sizeParameter, _expression, _comment, _invariant)

    def isRecordable(self):
        """
        Returns whether the declaration is recordable or not.
        :return: True if recordable, else False.
        :rtype: bool
        """
        return self.__isRecordable

    def isFunction(self):
        """
        Returns whether the declaration is a function or not.
        :return: True if function, else False.
        :rtype: bool
        """
        return self.__isFunction

    def getVariables(self):
        """
        Returns the set of left-hand side variables.
        :return: a list of variables.
        :rtype: list(ASTVariables)
        """
        return self.__variables

    def getDataType(self):
        """
        Returns the data type.
        :return: a data type object.
        :rtype: ASTDataType
        """
        return self.__dataType

    def hasSizeParameter(self):
        """
        Returns whether the declaration has a size parameter or not.
        :return: True if has size parameter, else False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def getSizeParameter(self):
        """
        Returns the size parameter.
        :return: the size parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def hasExpression(self):
        """
        Returns whether the declaration has a right-hand side expression or not.
        :return: True if right-hand side expression declared, else False.
        :rtype: bool
        """
        return self.__expression is not None

    def getExpr(self):
        """
        Returns the right-hand side expression.
        :return: the right-hand side expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def hasComment(self):
        """
        Returns whether declaration has a comment.
        :return: True if has comment, otherwise False.
        :rtype: bool
        """
        return self.__comment is not None

    def getComment(self):
        """
        Returns the comment.
        :return: the comment.
        :rtype: str
        """
        return self.__comment

    def hasInvariant(self):
        """
        Returns whether the declaration has a invariant or not.
        :return: True if has invariant, otherwise False.
        :rtype: bool
        """
        return self.__invariant is not None

    def getInvariant(self):
        """
        Returns the invariant.
        :return: the invariant
        :rtype: ASTExpression
        """
        return self.__invariant
