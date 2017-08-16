"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTDatatype import ASTDatatype

class ASTParameter:
    """
    This class is used to store a single function parameter definition.
    ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
    Grammar:
        parameter : NAME datatype;
    """
    __name = None
    __dataType = None

    def __init__(self, _name: str = None, _dataType: ASTDatatype = None):
        """
        Standard constructor.
        :param _name: the name of the parameter.
        :type _name: str
        :param _dataType: the type of the parameter. 
        :type _dataType: ASTDatatype
        """
        self.__dataType = _dataType
        self.__name = _name

    @classmethod
    def makeASTParameter(cls, _name: str = None, _dataType: ASTDatatype = None):
        """
        The factory method of the ASTParameter class.
        :param _name: the name of the parameter.
        :type _name: str
        :param _dataType: the type of the parameter. 
        :type _dataType: ASTDatatype
        :return: a new ASTParameter object.
        :rtype: ASTParameter
        """
        return cls(_name, _dataType)

    def getName(self) -> str:
        """
        Returns the name of the parameter.
        :return: the name of the parameter.
        :rtype: str
        """
        return self.__name

    def getDataType(self):
        """
        Returns the data type of the parameter.
        :return: the data type of the parameter.
        :rtype: ASTDataType
        """
        return self.__dataType
