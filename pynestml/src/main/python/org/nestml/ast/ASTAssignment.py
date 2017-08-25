"""
@author kperun
TODO header
"""


class ASTAssignment:
    """
    This class is used to store assignments.
    Grammar:
        assignment : lhsVariable=variable
            (directAssignment='='       |
            compoundSum='+='     |
            compoundMinus='-='   |
            compoundProduct='*=' |
            compoundQuotient='/=') expression;
    """
    __lhsVariable = None
    __isDirectAssignment = False
    __isCompoundSum = False
    __isCompoundMinus = False
    __isCompoundProduct = False
    __isCompoundQuotient = False
    __expression = None

    def __init__(self, _lhs=None, _isDirectAssignment=False, _isCompoundSum=False, _isCompoundMinus=False,
                 _isCompoundProduct=False, _isCompoundQuotient=False, _expression=None):
        """
        Standard constructor.
        :param _lhs: the left-hand side variable to which is assigned to.
        :type _lhs: ASTVariable 
        :param _isDirectAssignment: is a direct assignment
        :type _isDirectAssignment: bool 
        :param _isCompoundSum: is a compound sum
        :type _isCompoundSum: bool 
        :param _isCompoundMinus: is a compound minus
        :type _isCompoundMinus: bool
        :param _isCompoundProduct: is a compound product
        :type _isCompoundProduct: bool
        :param _isCompoundQuotient: is a compound quotient
        :type _isCompoundQuotient: bool
        :param _expression: an ast-expression object
        :type _expression: ASTExpression
        """
        self.__lhsVariable = _lhs
        self.__isDirectAssignment = _isDirectAssignment
        self.__isCompoundSum = _isCompoundSum
        self.__isCompoundMinus = _isCompoundMinus
        self.__isCompoundProduct = _isCompoundProduct
        self.__isCompoundQuotient = _isCompoundQuotient
        self.__expression = _expression

    @classmethod
    def makeASTAssignment(cls, _lhs=None, _isDirectAssignment=False, _isCompoundSum=False, _isCompoundMinus=False,
                          _isCompoundProduct=False, _isCompoundQuotient=False, _expression=None):
        """
        The factory method of the ASTAssignment class.
        :param _lhs: the left-hand side variable to which is assigned to.
        :type _lhs: ASTVariable 
        :param _isDirectAssignment: is a direct assignment
        :type _isDirectAssignment: bool 
        :param _isCompoundSum: is a compound sum
        :type _isCompoundSum: bool 
        :param _isCompoundMinus: is a compound minus
        :type _isCompoundMinus: bool
        :param _isCompoundProduct: is a compound product
        :type _isCompoundProduct: bool
        :param _isCompoundQuotient: is a compound quotient
        :type _isCompoundQuotient: bool
        :param _expression: an ast-expr object
        :type _expression: ASTExpr
        :return: a new ASTAssignment object.
        :rtype: ASTAssignment
        """
        return cls(_lhs, _isDirectAssignment, _isCompoundSum, _isCompoundMinus, _isCompoundProduct, _isCompoundQuotient,
                   _expression)

    def getVariable(self):
        """
        Returns the left-hand side variable.
        :return: left-hand side variable object.
        :rtype: ASTVariable
        """
        return self.__lhsVariable

    def isDirectAssignment(self):
        """
        Returns whether it is a direct assignment, e.g., V_m = 10mV
        :return: True if direct assignment, else False.
        :rtype: bool
        """
        return self.__isDirectAssignment

    def isCompoundSum(self):
        """
        Returns whether it is a compound sum, e.g., V_m += 10mV
        :return: True if compound sum, else False.
        :rtype: bool
        """
        return self.__isCompoundSum

    def isCompoundMinus(self):
        """
        Returns whether it is a compound minus, e.g., V_m -= 10mV
        :return: True if compound sum, else False.
        :rtype: bool
        """
        return self.__isCompoundMinus

    def isCompoundProduct(self):
        """
        Returns whether it is a compound product, e.g., V_m *= 10mV
        :return: True if compound sum, else False.
        :rtype: bool
        """
        return self.__isCompoundProduct

    def isCompoundQuotient(self):
        """
        Returns whether it is a compound quotient, e.g., V_m /= 10mV
        :return: True if compound sum, else False.
        :rtype: bool
        """
        return self.__isCompoundQuotient

    def getExpression(self):
        """
        Returns the right-hand side expression.
        :return: expression object.
        :rtype: ASTExpression
        """
        return self.__expression

    def printAST(self):
        """
        Returns a string representing the assignment.
        :return: a string representing the assignment.
        :rtype: str
        """
        ret = self.__lhsVariable.printAST()
        if self.isCompoundQuotient():
            ret += '/='
        elif self.isCompoundProduct():
            ret += '*='
        elif self.isCompoundMinus():
            ret += '-='
        elif self.isCompoundSum():
            ret += '+='
        else:
            ret += '='
        ret += self.__expression.printAST()
        return ret
