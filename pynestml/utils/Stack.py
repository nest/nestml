#
# Stack.py
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


class Stack(object):
    """
    This class represents a simple version of a stack.
    """
    __list = None
    __currentIndex = 0

    def __init__(self):
        """
        Standard constructor.
        """
        self.__list = list()
        self.__currentIndex = 0
        return

    def push(self,_elem=None):
        """
        Pushes an element to the stack
        :param _elem: a single element
        :type _elem: object
        """
        self.__currentIndex += 1
        self.__list.append(_elem)
        return

    def pop(self):
        """
        Returns the last element on the stack.
        :return: a single object if not empty, otherwise None
        :rtype: object
        """
        if self.isEmpty():
           return None
        else:
            temp = self.__list[self.__currentIndex]
            self.__currentIndex -=1
            self.__list.remove(temp)
            return temp

    def isEmpty(self):
        """
        Returns true if this stack is empty.
        :return: True if empty, otherwise False.
        :rtype: bool
        """
        return len(self.__list)


