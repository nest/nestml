"""
TODO header
@author kperun
"""


class ASTDerivative:
    """
    This class is used to store a derivative, e.g., V_m'.
    Grammar:
        derivative : name=NAME (differentialOrder='\'')*;
    """
    __name = None
    __differentialOrder = None

    def __init__(self, _name=None, _differentialOrder=0):
        """
        Standard constructor.
        :param _name: the name of the variable.
        :type _name: str
        :param _differentialOrder: the differential order of the variable
        :type _differentialOrder: int 
        """
        assert (_differentialOrder >= 0)
        self.__differentialOrder = _differentialOrder
        self.__name = _name

    @classmethod
    def makeASTDerivative(cls, _name=None, _differentialOrder=0):
        """
         A factory method used to generate new ASTDerivative.
        :param _name: the name of the variable.
        :type _name: str
        :param _differentialOrder: the differential order of the variable
        :type _differentialOrder: int 
        :return: a new ASTDerivative object.
        :rtype: ASTDerivative
        """
        return cls(_name, _differentialOrder)

    def getName(self):
        """
        Returns the name of the derivative.
        :return: the name. 
        :rtype: str
        """
        return self.__name

    def getDifferentialOrder(self):
        """
        Returns the differential order of the derivative.
        :return: the order of the variable.
        :rtype: int
        """
        return self.__differentialOrder
