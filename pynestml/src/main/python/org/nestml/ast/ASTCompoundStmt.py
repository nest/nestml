#
# ASTCompoundStmt.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement
from pynestml.src.main.python.org.nestml.ast.ASTIfStmt import ASTIfStmt
from pynestml.src.main.python.org.nestml.ast.ASTWhileStmt import ASTWhileStmt
from pynestml.src.main.python.org.nestml.ast.ASTForStmt import ASTForStmt


class ASTCompoundStmt(ASTElement):
    """
    This class is used to store compound statements.
    Grammar:
        compoundStmt : ifStmt
                | forStmt
                | whileStmt;
    """
    __ifStmt = None
    __whileStmt = None
    __forStmt = None

    def __init__(self, _ifStmt=None, _whileStmt=None, _forStmt=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _ifStmt: a if statement object
        :type _ifStmt: ASTIfStmt
        :param _whileStmt: a while statement object
        :type _whileStmt: ASTWhileStmt
        :param _forStmt: a for statement object
        :type _forStmt: ASTForStmt
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        """
        super(ASTCompoundStmt, self).__init__(_sourcePosition)
        assert (_ifStmt is None or isinstance(_ifStmt, ASTIfStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of if-statement handed over!'
        assert (_whileStmt is None or isinstance(_whileStmt, ASTWhileStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of while-statement handed over!'
        assert (_forStmt is None or isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of for-statement handed over!'
        self.__ifStmt = _ifStmt
        self.__whileStmt = _whileStmt
        self.__forStmt = _forStmt

    @classmethod
    def makeASTCompoundStmt(cls, _ifStmt=None, _whileStmt=None,
                            _forStmt=None, _sourcePosition=None):
        """
        Factory method of the ASTCompound_Stmt class.
        :param _ifStmt: a if statement object
        :type _ifStmt: ASTIfStmt
        :param _whileStmt: a while statement object
        :type _whileStmt: ASTWhileStmt
        :param _forStmt: a for statement object
        :type _forStmt: ASTForStmt
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        :return: a new compound statement object
        :rtype: ASTCompoundStmt
        """
        return cls(_ifStmt, _whileStmt, _forStmt, _sourcePosition)

    def isIfStmt(self):
        """
        Returns whether it is an "if" statement or not.
        :return: True if if stmt, False else.
        :rtype: bool
        """
        return self.__ifStmt is not None

    def getIfStmt(self):
        """
        Returns the "if" statement.
        :return: the "if" statement.
        :rtype: ASTIfStmt
        """
        return self.__ifStmt

    def isWhileStmt(self):
        """
        Returns whether it is an "while" statement or not.
        :return: True if "while" stmt, False else.
        :rtype: bool
        """
        return self.__whileStmt is not None

    def getWhileStmt(self):
        """
        Returns the while statement.
        :return: the while statement.
        :rtype: ASTWhileStmt
        """
        return self.__whileStmt

    def isForStmt(self):
        """
        Returns whether it is an "for" statement or not.
        :return: True if "for" stmt, False else.
        :rtype: bool
        """
        return self.__forStmt is not None

    def getForStmt(self):
        """
        Returns the for statement.
        :return: the for statement.
        :rtype: ASTForStmt
        """
        return self.__forStmt

    def printAST(self):
        """
        Returns a string representation of the compound statement.
        :return: a string representing the compound statement.
        :rtype: str
        """
        if self.isIfStmt():
            return self.getIfStmt().printAST()
        elif self.isForStmt():
            return self.getForStmt().printAST()
        elif self.isWhileStmt():
            return self.getWhileStmt().printAST()
        else:
            return '(NESTML.AST.CompoundStmt.Print) Unknown compound statement element.'
