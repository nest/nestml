# -*- coding: utf-8 -*-
#
# stack.py
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

    def __init__(self):
        """
        Standard constructor.
        """
        self.list = list()
        self.currentIndex = -1
        return

    def push(self, elem):
        """
        Pushes an element to the stack
        :param elem: a single element
        :type elem: object
        """
        self.currentIndex += 1
        self.list.append(elem)
        return

    def pop(self):
        """
        Returns the last element on the stack.
        :return: a single object if not empty, otherwise None
        :rtype: object
        """
        if self.is_empty():
            return None
        else:
            temp = self.list[self.currentIndex]
            self.currentIndex -= 1
            self.list.remove(temp)
            return temp

    def is_empty(self):
        """
        Returns true if this stack is empty.
        :return: True if empty, otherwise False.
        :rtype: bool
        """
        return len(self.list) == 0

    def top(self):
        return self.list[self.currentIndex]

    def pop_n_to_list(self, n):
        """
        Pops the first n items and returns them in a list
        :param n: the number of items
        :return: int
        """
        ret = list()
        for i in range(0, n):
            ret.append(self.pop())
        return ret

    def pop_n_first_to_list(self, n):
        """
        Pops the first n items and returns them in a list
        :param n: the number of items
        :return: int
        """
        ret = list()
        for i in range(0, n):
            ret.append(self.pop_first())
        return ret

    def pop_first(self):
        """
        Returns the first element on the stack.
        :return: a single object if not empty, otherwise None
        :rtype: object
        """
        if self.is_empty():
            return None
        else:
            temp = self.list[0]
            self.currentIndex = self.currentIndex - 1
            self.list.remove(temp)
            return temp
