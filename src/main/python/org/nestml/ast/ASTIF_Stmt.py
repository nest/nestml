"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTIF_Clause import ASTIF_Clause
from src.main.python.org.nestml.ast.ASTELSE_Clause import ASTELSE_Clause
from src.main.python.org.nestml.ast.ASTELIF_Clause import ASTELIF_Clause


class ASTIF_Stmt:
    """
    This class is used to store a single if block.
    Grammar:
        if_Stmt : if_Clause
                    elif_Clause*
                    (else_Clause)?
                    BLOCK_CLOSE;
    """
    __ifClause = None
    __elifClauses = None
    __elseClause = None

    def __init__(self, _ifClause: ASTIF_Clause = None, _elifClauses: list = list(),
                 _elseClause: ASTELSE_Clause = None):
        """
        Standard construcotr.
        :param _ifClause: the if clause
        :type _ifClause: ASTIF_Clause
        :param _elifClauses: (optional) list of elif clauses
        :type _elifClauses: ASTELIF_Clause
        :param _elseClause: (optional) else clause
        :type _elseClause: ASTELSE_Clause
        """
        self.__elseClause = _elseClause
        self.__ifClause = _ifClause
        self.__elifClauses = _elifClauses

    @classmethod
    def makeASTIF_Stmt(cls, _ifClause: ASTIF_Clause = None, _elifClauses: list = list(),
                       _elseClause: ASTELSE_Clause = None):
        """
        The factory method of the ASTIF_Stmt class.
        :param _ifClause: the if clause
        :type _ifClause: ASTIF_Clause
        :param _elifClauses: (optional) list of elif clauses
        :type _elifClauses: ASTELIF_Clause
        :param _elseClause: (optional) else clause
        :type _elseClause: ASTELSE_Clause
        :return: a new ASTIF_Stmt object
        :rtype: ASTIF_Stmt
        """
        assert (_ifClause is not None)  # at least the if-clause has to be given
        return cls(_ifClause, _elifClauses, _elseClause)

    def getIfClause(self):
        """
        Returns the if-clause.
        :return: the if clause
        :rtype: ASTIF_Clause
        """
        return self.__ifClause

    def hasElifClauses(self) -> bool:
        """
        Returns whether object contains elif clauses.
        :return: True if at leas one elif clause, False else.
        :rtype: bool
        """
        return len(self.__elifClauses) > 0

    def getElifClauses(self):
        """
        Returns a list of elif-clauses.
        :return: a list of elif-clauses.
        :rtype: list(ASTELIF_Clause)
        """
        return self.__elifClauses

    def hasElseClause(self) -> bool:
        """
        Returns whether object contains elif clauses.
        :return: True if object contains an else-clause, False else.
        :rtype: bool
        """
        return self.__elseClause is not None

    def getElseClause(self):
        """
        Returns the else-clause.
        :return: the else-clause.
        :rtype: ASTELSE_Clause
        """
        return self.__elseClause
