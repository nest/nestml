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
from pynestml.nestml.ASTElement import ASTElement
from pynestml.nestml.ASTIfStmt import ASTIfStmt
from pynestml.nestml.ASTWhileStmt import ASTWhileStmt
from pynestml.nestml.ASTForStmt import ASTForStmt


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
        assert (_ifStmt is None or isinstance(_ifStmt, ASTIfStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of if-statement provided (%s)!' % type(_ifStmt)
        assert (_whileStmt is None or isinstance(_whileStmt, ASTWhileStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of while-statement provided (%s)!' % type(_whileStmt)
        assert (_forStmt is None or isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.AST.CompoundStmt) Wrong type of for-statement provided (%s)!' % type(_forStmt)
        super(ASTCompoundStmt, self).__init__(_sourcePosition)
        self.__ifStmt = _ifStmt
        self.__whileStmt = _whileStmt
        self.__forStmt = _forStmt
        return

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
        return self.__ifStmt is not None and isinstance(self.__ifStmt, ASTIfStmt)

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
        return self.__whileStmt is not None and isinstance(self.__whileStmt, ASTWhileStmt)

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
        return self.__forStmt is not None and isinstance(self.__forStmt, ASTForStmt)

    def getForStmt(self):
        """
        Returns the for statement.
        :return: the for statement.
        :rtype: ASTForStmt
        """
        return self.__forStmt

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.isIfStmt():
            if self.getIfStmt() is _ast:
                return self
            elif self.getIfStmt().getParent(_ast) is not None:
                return self.getIfStmt().getParent(_ast)
        if self.isWhileStmt():
            if self.getWhileStmt() is _ast:
                return self
            elif self.getWhileStmt().getParent(_ast) is not None:
                return self.getWhileStmt().getParent(_ast)
        if self.isForStmt():
            if self.isForStmt() is _ast:
                return self
            elif self.getForStmt().getParent(_ast) is not None:
                return self.getForStmt().getParent(_ast)
        return None

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTCompoundStmt):
            return False
        if self.getForStmt() is not None and _other.getForStmt() is not None and \
                not self.getForStmt().equals(_other.getForStmt()):
            return False
        if self.getWhileStmt() is not None and _other.getWhileStmt() is not None and \
                not self.getWhileStmt().equals(_other.getWhileStmt()):
            return False
        if self.getIfStmt() is not None and _other.getIfStmt() is not None and \
                not self.getIfStmt().equals(_other.getIfStmt()):
            return False
        return True

    def __str__(self):
        """
        Returns a string representation of the compound statement.
        :return: a string representing the compound statement.
        :rtype: str
        """
        if self.isIfStmt():
            return str(self.getIfStmt())
        elif self.isForStmt():
            return str(self.getForStmt())
        elif self.isWhileStmt():
            return str(self.getWhileStmt())
        else:
            raise RuntimeError('Type of compound statement not specified!')
