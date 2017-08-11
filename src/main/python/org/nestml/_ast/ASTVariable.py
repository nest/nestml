"""
@author kperun
TODO header
"""


class ASTVariable:
    """
    This class is used to store a single variable.
    
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name
    Grammar:
        variable : NAME (differentialOrder='\'')*;
    """
    __name = None
    __differentialOrder = None

    def __init__(self, _name: str = None, _differentialOrder: int = 0):
        """
        Standard constructor.
        :param _name: the name of the variable
        :type _name: str
        :param _differentialOrder: the differential order of the variable.
        :type _differentialOrder: int
        """
        assert _differentialOrder > 0, "(NESTML) Differential order must be at least 0, is %d" % _differentialOrder
        assert _name is not None, "(NESTML) Name of variable must not be None"
        self.__name = _name
        self.__differentialOrder = _differentialOrder

    @classmethod
    def makeASTVariable(cls,_name: str = None, _differentialOrder: int = 0):
        """
        The factory method of the ASTVariable class.
        :param _name: the name of the variable
        :type _name: str
        :param _differentialOrder: the differential order of the variable.
        :type _differentialOrder: int
        :return: a new ASTVariable object.
        :rtype: ASTVariable
        """
        return cls(_name,_differentialOrder)

    def getName(self) -> str:
        """
        Returns the name of the variable.
        :return: the name of the variable.
        :rtype: str
        """
        return self.__name

    def getDifferentialOrder(self) -> int:
        """
        Returns the differential order of the variable.
        :return: the differential order.
        :rtype: int
        """
        return self.__differentialOrder