# -*- coding: utf-8 -*-
#
# co_co.py
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
from abc import ABCMeta, abstractmethod


class CoCo:
    """
    This class represents an abstract super-class for all concrete context conditions to check. All concrete CoCos
    have to inherit from this class. Hereby, the description can be used to state the condition the CoCo checks.
    Attributes:
        description type(str): This field can be used to give a short description regarding the properties which
                                are checked by this coco.
    """
    __metaclass__ = ABCMeta
    description = None

    @abstractmethod
    def check_co_co(self, node):
        """
        This is an abstract method which should be implemented by all concrete cocos.
        :param node: a single neuron instance on which the coco will be checked.
        :type node: ast_neuron
        :return: True, if CoCo holds, otherwise False.
        :rtype: bool
        """
        pass
