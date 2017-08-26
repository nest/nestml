"""
@author kperun
TODO header
"""


class ASTFunction:
    """
    This class is used to store a user-defined function.
    ASTFunction a function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name Functionname.
    @attribute parameters List with function parameters.
    @attribute returnType Complex return type, e.g. String
    @attribute primitiveType Primitive return type, e.g. int
    @attribute block Implementation of the function.
    Grammar:
    function: 'function' NAME '(' parameters? ')' (returnType=datatype)?
                   BLOCK_OPEN
                     block
                   BLOCK_CLOSE;
    """
    __name = None
    __parameters = None
    __returnType = None
    __block = None

    def __init__(self, _name=None, _parameters=None, _returnType=None, _block=None):
        """
        Standard constructor.
        :param _name: the name of the defined function.
        :type _name: str 
        :param _parameters: (Optional) Set of parameters.  
        :type _parameters: ASTParameters
        :param _returnType: (Optional) Return type. 
        :type _returnType: ASTDataType
        :param _block: a block of declarations.
        :type _block: ASTBlock
        """
        assert (_name is not None)
        assert (_block is not None)
        self.__block = _block
        self.__returnType = _returnType
        self.__parameters = _parameters
        self.__name = _name

    @classmethod
    def makeASTFunction(cls, _name=None, _parameters=None, _returnType=None, _block=None):
        """
        Factory method of the ASTFunction class.
        :param _name: the name of the defined function.
        :type _name: str 
        :param _parameters: (Optional) Set of parameters.  
        :type _parameters: ASTParameters
        :param _returnType: (Optional) Return type. 
        :type _returnType: ASTDataType
        :param _block: a block of declarations.
        :type _block: ASTBlock
        :return: a new ASTFunction object.
        :rtype: ASTFunction
        """
        return cls(_name, _parameters, _returnType, _block)

    def getName(self):
        """
        Returns the name of the function.
        :return: the name of the function.
        :rtype: str
        """
        return self.__name

    def hasParameters(self):
        """
        Returns whether parameters have been defined.
        :return: True if parameters defined, otherwise False.
        :rtype: bool
        """
        return (self.__parameters is not None) and (len(self.__parameters.getParametersList()) > 0)

    def getParameters(self):
        """
        Returns the list of parameters.
        :return: a parameters object containing the list.
        :rtype: ASTParameters
        """
        return self.__parameters

    def hasReturnType(self):
        """
        Returns whether return a type has been defined.
        :return: True if return type defined, otherwise False.
        :rtype: bool
        """
        return self.__returnType is not None

    def getReturnType(self):
        """
        Returns the return type of function.
        :return: the return type 
        :rtype: ASTDataType
        """
        return self.__returnType

    def getBlock(self):
        """
        Returns the block containing the definitions.
        :return: the block of the definitions.
        :rtype: ASTBlock
        """
        return self.__block

    def printAST(self):
        """
        Returns a string representation of the function defintion.
        :return: a string representation.
        :rtype: str
        """
        ret = 'function ' + self.getName() + '('
        if self.hasParameters():
            ret += self.getParameters().printAST()
        ret += ')'
        if self.hasReturnType():
            ret += self.getReturnType().printAST()
        ret += ':\n' + self.getBlock().printAST() + '\nend'
        return ret
