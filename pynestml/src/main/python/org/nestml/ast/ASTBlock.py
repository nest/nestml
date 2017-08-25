"""
@author kperun
TODO header
"""


class ASTBlock:
    """
    This class is used to store a single block of declarations, i.e., statements.
    Grammar:
        block : ( stmt | NEWLINE )*;
    """
    __stmts = None

    def __init__(self, _stmts=list()):
        """
        Standard constructor.
        :param _stmts: a list of statements 
        :type _stmts: list(ASTStmt)
        """
        self.__stmts = _stmts

    @classmethod
    def makeASTBlock(cls, _stmts=list()):
        """
        Factory method of ASTBlock.
        :param _stmts: a list of statements 
        :type _stmts: list(ASTStmt)
        """
        return cls(_stmts)

    def getStmts(self):
        """
        Returns the list of statements.
        :return: list of stmts.
        :rtype: list(ASTStmt)
        """
        return self.__stmts

    def addStmt(self, _stmt=None):
        """
        Adds a single statement to the list of statements.
        :param _stmt: a statement
        :type _stmt: ASTStmt
        :return: no value returned
        :rtype: None
        """
        self.__stmts.append(_stmt)

    def deleteStmt(self, _stmt=None):
        """
        Deletes the handed over statement.
        :param _stmt: 
        :type _stmt: 
        :return: True if deleted, otherwise False.
        :rtype: bool
        """
        self.__stmts.remove(_stmt)

    def printAST(self):
        """
        Returns the raw representation of the block as a string.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        for stmt in self.__stmts:
            ret += stmt.printAST()
            ret += '\n'
        return ret
