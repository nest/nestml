# -*- coding: utf-8 -*-
#
# either.py
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


class Either(object):
    """
    Objects of these class are either values or error messages.
    Attributes:
        __value (object): The value.
        __error (str): An error message.
    """

    def __init__(self, value=None, error=None):
        """
        Constructor for Either. Do not call directly! Use Either.value() or Either.error instead!
        :param value: a value
        :type value: object
        :param error: an error
        :type error: object
        """
        self.__value = value
        self.__error = error
        return

    @classmethod
    def value(cls, value):
        """
        Construct an Either holding a valid value
        :param value: the value to hold
        :type: _value: anything
        :return: an Either object holding a valid value
        :rtype: Either
        """
        return Either(value, None)

    @classmethod
    def error(cls, error):
        """
        Construct an Either holding an error message
        :param error: an error message
        :type error: str
        :return: an Either object holding an error message
        :rtype: Either
        """
        return Either(None, error)

    def get_value(self):
        """
        Get the valid value saved in the Either object
        :return: valid value
        :rtype: any type of valid values
        """
        return self.__value

    def get_error(self):
        """
        Get the error message saved in the Either object
        :return: an error message
        :rtype: str
        """
        return self.__error

    def is_value(self):
        """
        Return whether the object holds a valid value
        :return: true iff object holds a valid value
        :rtype: bool
        """
        return self.__value is not None

    def is_error(self):
        """
        Return whether the object holds an error message
        :return: true iff the object holds an error message
        :rtype: bool
        """
        return self.__error is not None

    def __str__(self):
        """
        Constructs string representation of the Either object
        :return: string representation of the object
        :rtype: str
        """
        return '(' + str(self.__value) + ', ' + str(self.__error) + ')'
