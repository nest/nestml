"""
@author kperun
TODO header
"""


class ASTBody:
    """
    This class is used to store the body of a neuron, an object containing all the definitions.
    ASTBody The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        body : BLOCK_OPEN
               (NEWLINE | var_Block | dynamics | equations | inputBuffer | outputBuffer | function)*
               BLOCK_CLOSE;        
    """
    __bodyElements = None

    def __init__(self, _bodyElements=list()):
        """
        Standard constructor.
        :param _bodyElements: a list of elements, e.g. variable blocks.
        :type _bodyElements: list()
        """
        self.__bodyElements = _bodyElements

    @classmethod
    def makeASTBody(cls, _bodyElements=list()):
        """
        Factory method of the ASTBody class.
        :param _bodyElements: a list of elements, e.g. variable blocks.
        :type _bodyElements: list()
        :return: a new body object.
        :rtype: ASTBody
        """
        return cls(_bodyElements)

    def getBodyElements(self):
        """
        Returns the list of body elements.
        :return: a list of body elements.
        :rtype: list()
        """
        return self.__bodyElements
