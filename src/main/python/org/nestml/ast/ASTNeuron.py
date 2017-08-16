"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTBody import ASTBody


class ASTNeuron:
    """
    This class is used to store instances of neurons.
    ASTNeuron represents neuron.
    @attribute Name    The name of the neuron
    @attribute Body    The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        neuron : 'neuron' NAME body;
    """
    __name = None
    __body = None

    def __init__(self, _name: str = None, _body: ASTBody = None):
        """
        Standard constructor.
        :param _name: the name of the neuron.
        :type _name: str
        :param _body: the body containing the defitions.
        :type _body: ASTBody
        """
        self.__name = _name
        self.__body = _body

    @classmethod
    def makeASTNeuron(cls, _name: str = None, _body: ASTBody = None):
        """
        Factory method of the ASTNeuron class.
        :param _name: the name of the neuron
        :type _name: str
        :param _body: the body containing the definitions.
        :type _body: ASTBody
        :return: a new ASTNeuron object.
        :rtype: ASTNeuron
        """
        assert (_name is not None)
        assert (_body is not None)
        return cls(_name, _body)

    def getName(self) -> str:
        """
        Returns the name of the neuron.
        :return: the name of the neuron.
        :rtype: str
        """
        return self.__name

    def getBody(self) -> str:
        """
        Return the body of the neuron.
        :return: the body containing the definitions.
        :rtype: ASTBody
        """
        return self.__body
