"""
@author kperun
TODO header
"""
import ASTInputType


class ASTInputLine:
    """
    This class is used to store a declaration of an input line.
    ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike

    @attribute sizeParameter Optional parameter representing  multisynapse neuron.
    @attribute sizeParameter Type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute spike true iff the neuron is a spike.
    @attribute current true iff. the neuron is a current.
    Grammar:
          inputLine :
                NAME
                ('[' sizeParameter=NAME ']')?
                '<-' inputType*
                ('spike' | 'current');
    """
    __name = None
    __sizeParameter = None
    __inputTypes = None
    __isSpike = False
    __isCurrent = False

    def __init__(self, _name: str = None, _sizeParameter: str = None, _inputTypes: list(ASTInputType) = list(),
                 _isSpike: bool = False, _isCurrent: bool = False):
        """
        Standard constructor.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _isSpike: is a spike buffer
        :type _isSpike: bool
        :param _isCurrent: is a current buffer
        :type _isCurrent: bool
        """
        assert (_name is not None)
        assert (_isSpike != _isCurrent)
        self.__isCurrent = _isCurrent
        self.__isSpike = _isSpike
        self.__inputTypes = _inputTypes
        self.__sizeParameter = _sizeParameter
        self.__name = _name

    @classmethod
    def makeASTInputLine(cls, _name: str = None, _sizeParameter: str = None, _inputTypes: list(ASTInputType) = list(),
                         _isSpike: bool = False, _isCurrent: bool = False):
        """
        Factory method of the ASTInputLine class.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _isSpike: is a spike buffer
        :type _isSpike: bool
        :param _isCurrent: is a current buffer
        :type _isCurrent: bool
        :return: a new ASTInputLine object.
        :rtype: ASTInputLine
        """
        return cls(_name, _sizeParameter, _inputTypes, _isSpike, _isCurrent)

    def getName(self) -> str:
        """
        Returns the name of the declared buffer.
        :return: the name.
        :rtype: str
        """
        return self.__name

    def hasIndexParameter(self) -> bool:
        """
        Returns whether a index parameter has been defined.
        :return: True if index has been used, otherwise False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def getIndexParameter(self) -> str:
        """
        Returns the index parameter.
        :return: the index parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def hasInputTypes(self) -> bool:
        """
        Returns whether input types have been defined.
        :return: True, if at least one input type has been defined.
        :rtype: bool
        """
        return len(self.__inputTypes) > 0

    def getInputTypes(self):
        """
        Returns the list of input types.
        :return: a list of input types.
        :rtype: list(ASTInputType)
        """
        return self.__inputTypes

    def isSpike(self) -> bool:
        """
        Returns whether this is a spike buffer or not.
        :return: True if spike buffer, False else.
        :rtype: bool 
        """
        return self.__isSpike

    def isSCurrent(self) -> bool:
        """
        Returns whether this is a current buffer or not.
        :return: True if current buffer, False else.
        :rtype: bool 
        """
        return self.__isCurrent
