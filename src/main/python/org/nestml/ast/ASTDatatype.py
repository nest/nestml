"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTUnitType import ASTUnitType


class ASTDatatype:
    """
    A datatype class as used to store a datatype of an element.
    ASTDatatype. Represents predefined datatypes and gives a possibility to use an unit
    datatype.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI datatype
    datatype : 'integer'
               | 'real'
               | 'string'
               | 'boolean'
               | 'void'
               | unitType;
    """
    __isInteger = False
    __isReal = False
    __isString = False
    __isBoolean = False
    __isVoid = False
    __isUnitType = None  # a unit type is not a boolean, but a concrete object

    def __init__(self, isInteger=False, isReal=False, isString=False, isBoolean=False, isVoid=False,
                 isUnitType: ASTUnitType = None):
        """
        :param isInteger: is an integer data type 
        :type isInteger: boolean
        :param isReal: is a real datatype 
        :type isReal: boolean
        :param isString: is a string data type
        :type isString: boolean
        :param isBoolean: is a boolean
        :type isBoolean: boolean
        :param isVoid: is a void data type
        :type isVoid: boolean
        :param isUnitType: an object of type ASTUnitType
        :type isUnitType: ASTUnitType
        """
        self.__isUnitType = isUnitType
        self.__isVoid = isVoid
        self.__isBoolean = isBoolean
        self.__isString = isString
        self.__isReal = isReal
        self.__isInteger = isInteger

    @classmethod
    def makeASTDatatype(cls, isInteger=False, isReal=False, isString=False,
                        isBoolean=False, isVoid=False, isUnitType: ASTUnitType = None):
        """
        A factory method for creation of objects of this class.
        :param isInteger: is an integer data type 
        :type isInteger: boolean
        :param isReal: is a real datatype 
        :type isReal: boolean
        :param isString: is a string data type
        :type isString: boolean
        :param isBoolean: is a boolean
        :type isBoolean: boolean
        :param isVoid: is a void data type
        :type isVoid: boolean
        :param isUnitType: an object of type ASTUnitType
        :type isUnitType: ASTUnitType
        """
        return cls(isInteger, isReal, isString, isBoolean, isVoid, isUnitType)

    def isInteger(self) -> bool:
        return self.__isInteger

    def isReal(self) -> bool:
        return self.__isReal

    def isString(self) -> bool:
        return self.__isString

    def isBoolean(self) -> bool:
        return self.__isBoolean

    def isVoid(self) -> bool:
        return self.__isVoid

    def isUnitType(self) -> bool:
        return self.__isUnitType is not None

    def getUnitType(self) -> ASTUnitType():
        return self.__isUnitType
