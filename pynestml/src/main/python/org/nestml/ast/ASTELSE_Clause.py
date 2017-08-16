"""
@author kperun
TODO Header
"""


class ASTELSE_Clause:
    """
    This class is used to store a single else-clause.
    Grammar:
        else_Clause : 'else' BLOCK_OPEN block;
    """
    __block = None

    def __init__(self, _block=None):
        """
        Standard constructor.
        :param _block: a block of statements.
        :type _block: ASTBlock
        """
        self.__block = _block

    @classmethod
    def makeASTELSE_Clause(cls, _block=None):
        """
        The factory method of the ASTELSE_Clause class.
        :param _block: a block of statements.
        :type _block: ASTBlock
        :return: a new block
        :rtype: ASTELSE_Clause
        """
        return cls(_block)

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block
