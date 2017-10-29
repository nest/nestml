#
# TypeChecker.py
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
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.TypeSymbol import TypeSymbol


class TypeChecker(object):
    # TODO change these to use equals()
    # TODO maybe migrate these to TypeSymbol?
    @classmethod
    def isNumeric(cls, _type=None):
        """
        Returns whether a typeSymbol is of a numeric type e.g. integer, real or unit
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.isInteger() or _type.isReal() or _type.hasUnit()

    @classmethod
    def isInteger(cls, _type=None):
        """
        Returns whether a typeSymbol identifies an integer
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.isInteger()

    @classmethod
    def isUnit(cls, _type=None):
        """
        Returns whether a typeSymbol identifies a Unit
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.hasUnit()

    @classmethod
    def isBoolean(cls, _type=None):
        """
        Returns whether a typeSymbol identifies a bool
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.equals(PredefinedTypes.getBooleanType())

    @classmethod
    def isReal(cls, _type=None):
        """
        Returns whether a typeSymbol identifies a real
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.equals(PredefinedTypes.getRealType())

    @classmethod
    def isString(cls, _type=None):
        """
        Returns whether a typeSymbol identifies a String
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.equals(PredefinedTypes.getStringType())

    @classmethod
    def isVoid(cls, _type=None):
        """
        Returns whether a typeSymbol identifies a String
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.equals(PredefinedTypes.getVoidType())

    @classmethod
    def isNumericPrimitive(cls, _type=None):
        """
        Returns whether a typeSymbol identifies primitive numeric unit (i.e. real or int)
        :param _type: the typeSymbol to check
        :type _type: TypeSymbol
        :return: bool
        """
        assert _type is not None
        assert isinstance(_type, TypeSymbol)
        return _type.isInteger() or _type.isReal()
