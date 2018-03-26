#
# ASTForStmt.py
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

from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class ASTForStmt(ASTNode):
    """
    This class is used to store a for-block.
    Grammar:
        forStmt : 'for' var=NAME 'in' vrom=expression
                    '...' to=expression 'step' step=signedNumericLiteral BLOCK_OPEN block BLOCK_CLOSE;
    """
    __variable = None
    __from = None
    __to = None
    __step = None
    __block = None

    def __init__(self, _variable=None, _from=None, _to=None, _step=0, _block=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _variable: the step variable used for iteration.
        :type _variable: str
        :param _from: left bound of the range, i.e., start value.
        :type _from: ASTExpression
        :param _to: right bound of the range, i.e., finish value.
        :type _to: ASTExpression
        :param _step: the length of a single step.
        :type _step: float/int
        :param _block: a block of statements.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_variable is not None and isinstance(_variable, str)), \
            '(PyNestML.AST.ForStmt) No or wrong type of iteration variable provided (%s)!' % type(_variable)
        assert (_from is not None and (isinstance(_from, ASTExpression) or
                                       isinstance(_from, ASTSimpleExpression))), \
            '(PyNestML.AST.ForStmt) No or wrong type of from-statement provided (%s)!' % type(_from)
        assert (_to is not None and (isinstance(_to, ASTExpression) or isinstance(_to, ASTSimpleExpression))), \
            '(PyNestML.AST.ForStmt) No or wrong type of to-statement provided (%s)!' % type(_to)
        assert (_step is not None and (isinstance(_step, int) or isinstance(_step, float))), \
            '(PyNestML.AST.ForStmt) No step size or wrong type provided (%s)!' % type(_step)
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.AST.ForStmt) No or wrong type of block provided (%s)!' % type(_block)
        super(ASTForStmt, self).__init__(_sourcePosition)
        self.__block = _block
        self.__step = _step
        self.__to = _to
        self.__from = _from
        self.__variable = _variable
        return

    @classmethod
    def makeASTForStmt(cls, _variable=None, _from=None, _to=None, _step=0, _block=None, _sourcePosition=None):
        """
        The factory method of the ASTForStmt class.
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
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTForStmt object.
        :rtype: ASTForStmt
        """
        return cls(_variable, _from, _to, _step, _block, _sourcePosition)

    def getVariable(self):
        """
        Returns the name of the step variable.
        :return: the name of the step variable.
        :rtype: str
        """
        return self.__variable

    def getFrom(self):
        """
        Returns the from-statement.
        :return: the expression indicating the start value.
        :rtype: ASTExpression
        """
        return self.__from

    def getTo(self):
        """
        Returns the to-statement.
        :return: the expression indicating the finish value.
        :rtype: ASTExpression
        """
        return self.__to

    def getStep(self):
        """
        Returns the length of a single step.
        :return: the length as a float.
        :rtype: float
        """
        return self.__step

    def getBlock(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.__block

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.getFrom() is _ast:
            return self
        elif self.getFrom().getParent(_ast) is not None:
            return self.getFrom().getParent(_ast)
        if self.getTo() is _ast:
            return self
        elif self.getTo().getParent(_ast) is not None:
            return self.getTo().getParent(_ast)
        if self.getBlock() is _ast:
            return self
        elif self.getBlock().getParent(_ast) is not None:
            return self.getBlock().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the for statement.
        :return: a string representing the for statement.
        :rtype: str
        """
        return 'for ' + self.getVariable() + ' in ' + str(self.getFrom()) + '...' \
               + str(self.getTo()) + ' step ' + str(self.getStep()) + ':\n' + str(self.getBlock()) + '\nend'

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTForStmt):
            return False
        if self.getVariable() != _other.getVariable():
            return False
        if not self.getFrom().equals(_other.getFrom()):
            return False
        if not self.getTo().equals(_other.getTo()):
            return False
        if self.getStep() != _other.getStep():
            return False
        return self.getBlock().equals(_other.getBlock())
