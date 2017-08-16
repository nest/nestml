"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTSmall_Stmt import ASTSmall_Stmt
from src.main.python.org.nestml.ast.ASTCompound_Stmt import ASTCompound_Stmt


class ASTStmt:
    """
    This class is used to store a single statement.
    """
    __small_statement = None
    __compound_statement = None

    def __init__(self, _small_statement: ASTSmall_Stmt = None, _compound_statement: ASTCompound_Stmt = None):
        """
        Standard constructor.
        :param _small_statement: a small statement
        :type _small_statement: ASTSmall_Stmt 
        :param _compound_statement: a compound statement
        :type _compound_statement: ASTCompound_Stmt
        """
        assert (_small_statement is None or _compound_statement is None)  # only of one type
        self.__small_statement = _small_statement
        self.__compound_statement = _compound_statement


    @classmethod
    def makeASTStmt(cls,_small_statement: ASTSmall_Stmt = None, _compound_statement: ASTCompound_Stmt = None):
        """
        Factory method of the ASTStmt class.
        :param _small_statement: a small statement.
        :type _small_statement: ASTSmall_Stmt
        :param _compound_statement: a compound statement
        :type _compound_statement: ASTCompound_Stmt
        :return: a new ASTStmt object
        :rtype: ASTStmt
        """
        return cls(_small_statement,_compound_statement)

    def isSmallStmt(self) -> bool:
        """
        Returns whether it is a small statement or not.
        :return: True if small stmt, False else.
        :rtype: bool
        """
        return self.__small_statement is not None

    def getSmallStmt(self):
        """
        Returns the small statement.
        :return: the small statement.
        :rtype: ASTSmall_Stmt
        """
        return self.__small_statement

    def isCompoundStmt(self) -> bool:
        """
        Returns whether it is a compound statement or not.
        :return: True if compound stmt, False else.
        :rtype: bool
        """
        return self.__compound_statement is not None

    def getCompoundStmt(self):
        """
        Returns the compound statement.
        :return: the compound statement.
        :rtype: ASTCompound_Stmt
        """
        return self.__compound_statement













