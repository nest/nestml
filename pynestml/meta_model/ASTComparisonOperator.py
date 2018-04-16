#
# ASTComparisonOperator.py
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
from pynestml.meta_model.ASTNode import ASTNode
from pynestml.utils.Logger import LoggingLevel, Logger


class ASTComparisonOperator(ASTNode):
    """
    This class is used to store a single comparison operator.
    Grammar:
        comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');
    """
    __isLt = False
    __isLe = False
    __isEq = False
    __isNe = False
    __isNe2 = False
    __isGe = False
    __isGt = False

    def __init__(self, _isLt=False, _isLe=False, _isEq=False, _isNe=False, _isNe2=False,
                 _isGe=False, _isGt=False, source_position=None):
        """
        Standard constructor.
        :param _isLt: is less than operator.
        :type _isLt: bool
        :param _isLe: is less equal operator.
        :type _isLe: bool
        :param _isEq: is equality operator.
        :type _isEq: bool
        :param _isNe: is not equal operator.
        :type _isNe: bool
        :param _isNe2: is not equal operator (alternative syntax).
        :type _isNe2: bool
        :param _isGe: is greater equal operator.
        :type _isGe: bool
        :param _isGt: is greater than operator.
        :type _isGt: bool
        :param _sourcePosition: the position of the element in the source
        :type source_position: ASTSourceLocation
        """
        assert (_isLt is not None and isinstance(_isLt, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-less-than operator provided (%s)!' % type(_isLt)
        assert (_isLe is not None and isinstance(_isLe, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-less-equal operator provided (%s)!' % type(_isLe)
        assert (_isEq is not None and isinstance(_isEq, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-equal operator provided (%s)!' % type(_isEq)
        assert (_isNe is not None and isinstance(_isNe, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-not-equal operator provided (%s)!' % type(_isNe)
        assert (_isNe2 is not None and isinstance(_isNe2, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-not-equal2 operator provided (%s)!' % type(_isNe2)
        assert (_isGe is not None and isinstance(_isGe, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-greater-equal operator provided (%s)!' % type(
                _isGe)
        assert (_isGt is not None and isinstance(_isGt, bool)), \
            '(PyNestML.AST.ComparisonOperator) No or wrong type of is-greater-than operator provided (%s)!' % type(
                _isGt)
        assert ((_isLt + _isLe + _isEq + _isNe + _isNe2 + _isGe + _isGt) == 1), \
            '(PyNestML.AST.ComparisonOperator) Comparison operator not correctly specified!'
        super(ASTComparisonOperator, self).__init__(source_position)
        self.__isGt = _isGt
        self.__isGe = _isGe
        self.__isNe2 = _isNe2
        self.__isNe = _isNe
        self.__isEq = _isEq
        self.__isLe = _isLe
        self.__isLt = _isLt
        return

    def isLt(self):
        """
        Returns whether it is the less than operator.
        :return: True if less than operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isLt, bool) and self.__isLt

    def isLe(self):
        """
        Returns whether it is the less equal operator.
        :return: True if less equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isLe, bool) and self.__isLe

    def isEq(self):
        """
        Returns whether it is the equality operator.
        :return: True if less equality operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isEq, bool) and self.__isEq

    def isNe(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isNe, bool) and self.__isNe

    def isNe2(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isNe2, bool) and self.__isNe2

    def isGe(self):
        """
        Returns whether it is the greater equal operator.
        :return: True if less greater operator, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isGe, bool) and self.__isGe

    def isGt(self):
        """
        Returns whether it is the greater than operator.
        :return: True if less greater than, otherwise False
        :rtype: bool
        """
        return isinstance(self.__isGt, bool) and self.__isGt

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def __str__(self):
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isLt:
            return ' < '
        elif self.__isLe:
            return ' <= '
        elif self.__isEq:
            return ' == '
        elif self.__isNe:
            return ' != '
        elif self.__isNe2:
            return ' <> '
        elif self.__isGe:
            return ' >= '
        elif self.__isGt:
            return ' > '
        else:
            Logger.log_message('Type of comparison operator not specified!', LoggingLevel.WARNING)

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTComparisonOperator):
            return False
        return self.isLt() == other.isLt() and self.isLe() == other.isLe() and \
               self.isEq() == other.isEq() and self.isNe() == other.isNe() and \
               self.isNe2() == other.isNe2() and self.isGe() == other.isGe() and self.isGt() == other.isGt()
