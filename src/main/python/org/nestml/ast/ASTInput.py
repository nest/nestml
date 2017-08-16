"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine


class ASTInput:
    """
    This class is used to store blocks of input definitions.
    ASTInput represents the input block:
        input:
          spikeBuffer   <- inhibitory excitatory spike
          currentBuffer <- current
        end

    @attribute inputLine set of input lines.
    Grammar:
          inputBuffer: 'input'
            BLOCK_OPEN
              (inputLine | NEWLINE)*
            BLOCK_CLOSE;
    """
    __inputDefinitions = None

    def __init__(self, _inputDefinitions: list = list()):
        """
        Standard constructor.
        :param _inputDefinitions: 
        :type _inputDefinitions: list(ASTInputLine) 
        """
        self.__inputDefinitions = _inputDefinitions

    @classmethod
    def makeASTInput(cls, _inputDefinitions: list = list()):
        """
        Factory method of the ASTInput class.
        :param _inputDefinitions: a list of input definitions.
        :type _inputDefinitions: list(ASTInputLine)
        :return: a new ASTInput object
        :rtype: ASTInput
        """
        return cls(_inputDefinitions)

    def getInputLines(self):
        """
        Returns the list of input lines.
        :return: a list of input lines
        :rtype: list(ASTInputLine)
        """
        return self.__inputDefinitions
