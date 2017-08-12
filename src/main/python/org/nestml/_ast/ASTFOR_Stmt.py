"""
@author kperun
TODO header
"""
import ASTExpression
import ASTBlock


class ASTFOR_Stmt:
    """
    This class is used to store a for-block.
    Grammar:
        for_Stmt : 'for' var=NAME 'in' vrom=expression 
                    '...' to=expression 'step' step=signedNumericLiteral BLOCK_OPEN block BLOCK_CLOSE;
    """
    __variable = None
    __from = None
    __to = None
    __step = None
    __block = None

    def __init__(self, _variable: str = None, _from: ASTExpression = None, _to: ASTExpression = None, _step: int = 0,
                 _block: ASTBlock = None):
        """
        Standard constructor.
        :param _variable: the step variable used for iteration.
        :type _variable: str
        :param _from: left bound of the range, i.e., start value.
        :type _from: ASTExpression
        :param _to: right bound of the range, i.e., finish value.
        :type _to: ASTExpression
        :param _step: the length of a single step.
        :type _step: int
        :param _block: a block of statements.
        :type _block: ASTBlock
        """
        self.__block = _block
        self.__step = _step
        self.__to = _to
        self.__from = _from
        self.__variable = _variable

    @classmethod
    def makeASTFOR_Stmt(cls, _variable: str = None, _from: ASTExpression = None, _to: ASTExpression = None, _step: float = 0,
                        _block: ASTBlock = None):
        """
        The factory method of the ASTFOR_Stmt class.
        :param _variable: the step variable used for iteration.
        :type _variable: str
        :param _from: left bound of the range, i.e., start value.
        :type _from: ASTExpression
        :param _to: right bound of the range, i.e., finish value.
        :type _to: ASTExpression
        :param _step: the length of a single step.
        :type _step: float
        :param _block: a block of statements.
        :type _block: ASTBlock 
        :return: a new ASTFOR_Stmt object.
        :rtype: ASTFOR_Stmt
        """
        return cls(_variable, _from, _to, _step, _block)

    def getVariable(self) -> str:
        """
        Returns the name of the step variable.
        :return: the name of the step variable.
        :rtype: str
        """
        return self.__variable

    def getFrom(self) -> ASTExpression:
        """
        Returns the from-statement.
        :return: the expression indicating the start value.
        :rtype: ASTExpression
        """
        return self.__from

    def getTo(self) -> ASTExpression:
        """
        Returns the to-statement.
        :return: the expression indicating the finish value.
        :rtype: ASTExpression
        """
        return self.__to

    def getStep(self) -> float:
        """
        Returns the length of a single step.
        :return: the length as a float.
        :rtype: float
        """
        return self.__step

    def getBlock(self) -> ASTBlock:
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block
