"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTIF_Stmt import ASTIF_Stmt
from src.main.python.org.nestml.ast.ASTWHILE_Stmt import ASTWHILE_Stmt
from src.main.python.org.nestml.ast.ASTFOR_Stmt import ASTFOR_Stmt


class ASTCompound_Stmt:
    """
    This class is used to store compound statements.
    Grammar:
        compound_Stmt : if_Stmt
                | for_Stmt
                | while_Stmt;
    """
    __if_stmt = None
    __while_stmt = None
    __for_stmt = None

    def __init__(self, _if_stmt: ASTIF_Stmt = None, _while_stmt: ASTWHILE_Stmt = None, _for_stmt: ASTFOR_Stmt = None):
        """
        Standard constructor.
        :param _if_stmt: a if statement object
        :type _if_stmt: ASTIF_Stmt
        :param _while_stmt: a while statement object
        :type _while_stmt: ASTWHILE_Stmt
        :param _for_stmt: a for statement object
        :type _for_stmt: ASTFOR_Stmt
        """
        self.__if_stmt = _if_stmt
        self.__while_stmt = _while_stmt
        self.__for_stmt = _for_stmt

    @classmethod
    def makeASTCompound_Stmt(cls, _if_stmt: ASTIF_Stmt = None, _while_stmt: ASTWHILE_Stmt = None,
                             _for_stmt: ASTFOR_Stmt = None):
        """
        Factory method of the ASTCompound_Stmt class.
        :param _if_stmt: a if statement object
        :type _if_stmt: ASTIF_Stmt
        :param _while_stmt: a while statement object
        :type _while_stmt: ASTWHILE_Stmt
        :param _for_stmt: a for statement object
        :type _for_stmt: ASTFOR_Stmt
        :return: a new compound_stmt object
        :rtype: ASTCompound_Stmt
        """
        return cls(_if_stmt,_while_stmt,_for_stmt)

    def isIfStmt(self) -> bool:
        """
        Returns whether it is an "if" statement or not.
        :return: True if if stmt, False else.
        :rtype: bool
        """
        return self.__if_stmt is not None

    def getIfStmt(self):
        """
        Returns the "if" statement.
        :return: the "if" statement.
        :rtype: ASTIF_Stmt
        """
        return self.__if_stmt

    def isWhileStmt(self) -> bool:
        """
        Returns whether it is an "while" statement or not.
        :return: True if "while" stmt, False else.
        :rtype: bool
        """
        return self.__while_stmt is not None

    def getWhileStmt(self):
        """
        Returns the while statement.
        :return: the while statement.
        :rtype: ASTWHILE_Stmt
        """
        return self.__while_stmt

    def isForStmt(self) -> bool:
        """
        Returns whether it is an "for" statement or not.
        :return: True if "for" stmt, False else.
        :rtype: bool
        """
        return self.__for_stmt is not None

    def getForStmt(self):
        """
        Returns the for statement.
        :return: the for statement.
        :rtype: ASTFOR_Stmt
        """
        return self.__for_stmt

