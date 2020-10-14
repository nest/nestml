# -*- coding: utf-8 -*-
#
# i_reference_converter.py
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


class IReferenceConverter(object):
    """This class represents a abstract super class for all possible reference converters, e.g. for nest, SpiNNaker or LEMS.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def convert_binary_op(self, binary_operator):
        pass

    @abstractmethod
    def convert_function_call(self, function_call, prefix=''):
        pass

    @abstractmethod
    def convert_name_reference(self, variable, prefix=''):
        pass

    @abstractmethod
    def convert_constant(self, constant_name):
        pass

    @abstractmethod
    def convert_unary_op(self, unary_operator):
        pass

    @abstractmethod
    def convert_encapsulated(self):
        pass

    @abstractmethod
    def convert_logical_not(self):
        pass

    @abstractmethod
    def convert_arithmetic_operator(self, op):
        pass

    @abstractmethod
    def convert_bit_operator(self, op):
        pass

    @abstractmethod
    def convert_comparison_operator(self, op):
        pass

    @abstractmethod
    def convert_logical_operator(self, op):
        pass

    @abstractmethod
    def convert_ternary_operator(self):
        pass
