"""
@author kperun
TODO header
"""


class ASTOutput:
    """
    This class is used to store output buffer declarations.
    ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    Grammar:
        outputBuffer: 'output' BLOCK_OPEN ('spike' | 'current') ;
    """
    __type = None

    def __init__(self, _type=None):
        """
        Standard constructor.
        :param _type: the type of the output buffer.
        :type _type: str
        """
        assert (_type is "spike" or _type is _type is "current"), '(NESTML) Wrong type (=%s) of buffer provided' % _type
        self.__type = _type

    @classmethod
    def makeASTOutput(cls, _type=None):
        """
        Factory method of the ASTOutput class.
        :param _type: the type of the output buffer.
        :type _type: str
        :return: a new ASTOutput object
        :rtype: ASTOutput
        """
        return cls(_type)

    def isSpike(self):
        """
        Returns whether it is a spike buffer or not.
        :return: True if spike, otherwise False.
        :rtype: bool
        """
        return self.__type is "spike"

    def isCurrent(self):
        """
        Returns whether it is a current buffer or not.
        :return: True if current, otherwise False.
        :rtype: bool
        """
        return self.__type is "current"
