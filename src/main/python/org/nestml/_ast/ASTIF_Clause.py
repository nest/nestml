"""
@author kperun
TODO header
"""
import ASTExpr
import ASTBlock


class ASTIF_Clause:
    """
    This class is used to store a single if-clause.
    Grammar:
        if_Clause : 'if' expr BLOCK_OPEN block;
    """
    __condition = None
    __block = None

    def __init__(self, _condition: ASTExpr = None, _block: ASTBlock = None):
        """
        Standard constructor.
        :param _condition: the condition of the block.
        :type _condition: ASTExpr
        :param _block: a block of statements.
        :type _block: ASTBlock
        """
        self.__block = _block
        self.__condition = _condition

    @classmethod
    def makeASTIF_Clause(cls, _condition: ASTExpr = None, _block: ASTBlock = None):
        """
        The factory method of the ASTIF_Clause class.
        :param _condition: the condition of the block.
        :type _condition: ASTExpr
        :param _block: a block of statements.
        :type _block: ASTBlock
        :return: a new block
        :rtype: ASTIF_Clause
        """
        return cls(_condition, _block)

    def getCondition(self):
        """
        Returns the condition of the block.
        :return: the condition.
        :rtype: ASTExpr
        """
        return self.__condition

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block
