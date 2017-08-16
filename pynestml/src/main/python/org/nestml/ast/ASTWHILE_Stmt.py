"""
@author kperun
TODO header
"""
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression
from pynestml.src.main.python.org.nestml.ast.ASTBlock import ASTBlock


class ASTWHILE_Stmt:
    """
    This class is used to store a new while-block.
    Grammar:
        while_Stmt : 'while' expr BLOCK_OPEN block BLOCK_CLOSE;
    """
    __condition = None
    __block = None

    def __init__(self, _condition=None, _block=None):
        """
        Standard constructor.
        :param _condition: the condition of the block.
        :type _condition: ASTExpression
        :param _block: a block of statements.
        :type _block: ASTBlock
        """
        self.__block = _block
        self.__condition = _condition

    @classmethod
    def makeASTWHILE_Stmt(cls, _condition=None, _block=None):
        """
        The factory method of the ASTWHILE_Stmt class.
        :param _condition: the condition of the block.
        :type _condition: ASTExpression
        :param _block: a block of statements.
        :type _block: ASTBlock
        :return: a new block
        :rtype: ASTWHILE_Stmt
        """
        assert (isinstance(_condition, ASTExpression)), '(PyNESTML.AST) Handed over object not an expression.'
        assert (isinstance(_block, ASTBlock)), '(PyNESTML.AST) Handed over object not a block.'
        return cls(_condition, _block)

    def getCondition(self):
        """
        Returns the condition of the block.
        :return: the condition.
        :rtype: ASTExpression
        """
        return self.__condition

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block
