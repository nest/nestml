#
# Either.py
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

"""
Objects of these class are either values or error messages

"""
class Either:
    __value = None
    __error = None

    def __init__(self, _value = None , _error = None):
        """
        Constructor for Either. Do not call directly! Use Either.value() or Either.error instead!
        """
        self.__value = _value
        self.__error = _error
        return

    @classmethod
    def value(cls, _value = None):
        """
        Construct an Either holding a valid value
        :param _value: the value to hold
        :type: _value: anything
        :return: an Either object holding a valid value
        :rtype: Either
        """
        assert _value is not None
        return Either(_value, None)

    @classmethod
    def error(cls, _error = None):
        """
        Construct an Either holding an error message
        :param _error: an error message
        :type _error: str
        :return: an Either object holding an error message
        :rtype: Either
        """
        assert _error is not None
        assert isinstance(_error,str)
        return Either(None, _error)

    def getValue(self):
        """
        Get the valid value saved in the Either object
        :return: valid value
        :rtype: any type of valid values
        """
        return self.__value

    def getError(self):
        """
        Get the error message saved in the Either object
        :return: an error message
        :rtype: str
        """
        return self.__error

    def isValue(self):
        """
        Return whether the object holds a valid value
        :return: true iff object holds a valid value
        :rtype: bool
        """
        return self.__value is not None

    def isError(self):
        """
        Return whether the object holds an error message
        :return: true iff the object holds an error message
        :rtype: bool
        """
        return self.__error is not None

    def printSelf(self):
        """
        Constructs string representation of the Either object
        :return: string representation of the object
        :rtype: str
        """
        return "(" + self.__value + ", " + self.__error + ")"