"""
@author kperun
TODO header
"""


class ASTInputType:
    """
    This class is used to store the type of a buffer.
    ASTInputType represents the type of the input line e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
    Grammar:
        inputType : ('inhibitory' | 'excitatory');
    """
    __isInhibitory = False
    __isExcitatory = False

    def __init__(self, _isInhibitory: bool = False, _isExcitatory: bool = False):
        """
        Standard constructor.
        :param _isInhibitory: is inhibitory buffer.
        :type _isInhibitory: bool
        :param _isExcitatory: is excitatory buffer.
        :type _isExcitatory: book
        """
        assert (_isExcitatory != _isInhibitory)
        self.__isExcitatory = _isExcitatory
        self.__isInhibitory = _isInhibitory

    @classmethod
    def makeASTInputType(cls, _isInhibitory: bool = False, _isExcitatory: bool = False):
        """
        Factory method of the ASTInputType class.
        :param _isInhibitory: is inhibitory buffer.
        :type _isInhibitory: bool
        :param _isExcitatory: is excitatory buffer.
        :type _isExcitatory: book
        :return: a new ASTInputType object.
        :rtype: ASTInputType
        """
        return cls(_isInhibitory, _isExcitatory)

    def isExcitatory(self) -> bool:
        """
        Returns whether it is excitatory type.
        :return: True if excitatory, otherwise False.
        :rtype: bool
        """
        return self.__isExcitatory

    def isInhibitory(self) -> bool:
        """
        Returns whether it is inhibitory type.
        :return: True if inhibitory , otherwise False.
        :rtype: bool
        """
        return self.__isInhibitory
