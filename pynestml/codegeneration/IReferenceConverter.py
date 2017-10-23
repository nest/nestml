#
# IReferenceConverter.py
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
from pynestml.nestml.ASTFunctionCall import ASTFunctionCall


class IReferenceConverter(object):
    """
    This class represents a abstract super class for all possible reference converters, e.g. for nest, spinnacker
    or lems.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def convertBinaryOp(self, _binaryOperator):
        pass

    @abstractmethod
    def convertFunctionCall(self, _astFunctionCall):
        pass

    @abstractmethod
    def convertNameReference(self, _astVariable):
        pass

    @abstractmethod
    def convertConstant(self, _constantName):
        pass

    @abstractmethod
    def convertUnaryOp(self,_unaryOperator):
        pass

    def needsArguments(self, _astFunctionCall):
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall))
        return len(_astFunctionCall.getArgs()) > 0
