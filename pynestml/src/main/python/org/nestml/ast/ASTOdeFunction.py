"""TODO header
@author kperun
"""


class ASTOdeFunction:
    """
    Stores a single declaration of a ode function, e.g., 
        function v_init mV = V_m - 50mV.
    """
    __isRecordable = False
    __variableName = None
    __dataType = None
    __expression = None

    def __init__(self, _isRecordable=False, _variableName=None, _dataType=None, _expression=None):
        """
        Standard constructor.
        :param _isRecordable: is this function recordable or not.
        :type _isRecordable: bool
        :param _variableName: the name of the variable.
        :type _variableName: str
        :param _dataType: the datatype of the function.
        :type _dataType: ASTDataType
        :param _expression: the computation expression.
        :type _expression: ASTExpression
        """
        self.__isRecordable = _isRecordable
        self.__variableName = _variableName
        self.__dataType = _dataType
        self.__expression = _expression

    @classmethod
    def makeASTOdeFunction(cls, _isRecordable=False, _variableName=None, _dataType=None, _expression=None):
        """
        A factory method used to generate new ASTOdeFunction.
        :param _isRecordable: is this function recordable or not.
        :type _isRecordable: bool
        :param _variableName: the name of the variable.
        :type _variableName: str
        :param _dataType: the datatype of the function.
        :type _dataType: ASTDataType
        :param _expression: the computation expression.
        :type _expression: ASTExpression
        """
        assert (_variableName is not None), '(NESTML) No variable name provided.'
        assert (_dataType is not None), '(NESTML) No variable datatype provided.'
        assert (_expression is not None), '(NESTML) No computation expression provided.'
        return cls(_isRecordable, _variableName, _dataType, _expression)

    def isRecordable(self):
        """
        Returns whether this ode function is recordable or not.
        :return: True if recordable, else False.
        :rtype: bool
        """
        return self.__isRecordable

    def getVariableName(self):
        """
        Returns the variable name.
        :return: the name of the variable.
        :rtype: str
        """
        return self.__variableName

    def getDataType(self):
        """
        Returns the data type as an object of ASTDatatype.
        :return: the type as an object of ASTDatatype.
        :rtype: ASTDatatype
        """
        return self.__dataType

    def getExpression(self):
        """
        Returns the expression as an object of ASTExpression.
        :return: the expression as an object of ASTExpression.
        :rtype: ASTExpression
        """
        return self.__dataType
