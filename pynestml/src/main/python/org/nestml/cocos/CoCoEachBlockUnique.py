#
# CoCoEachBlockUnique.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron


class CoCoEachBlockUnique(CoCo):
    """
    This context  condition ensures that each block is defined at most once.
    """

    def checkCoCo(self, _neuron=None):
        """
        Checks whether each block is define at most once.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.ElementDefined) No or wrong type of neuron provided!'
        if len(_neuron.getStateBlocks()) > 1:
            raise BlockNotUniqueException('State!')
        if len(_neuron.getUpdateBlocks()) > 1:
            raise BlockNotUniqueException('Update!')
        if len(_neuron.getParameterBlocks()) > 1:
            raise BlockNotUniqueException('Parameters!')
        if len(_neuron.getInternalsBlocks()) > 1:
            raise BlockNotUniqueException('Internals!')
        if len(_neuron.getEquationsBlocks()) > 1:
            raise BlockNotUniqueException('Equations!')
        if len(_neuron.getInputBlocks()) > 1:
            raise BlockNotUniqueException('Input!')
        if len(_neuron.getOutputBlocks()) > 1:
            raise BlockNotUniqueException('Output!')
        return


class BlockNotUniqueException(Exception):
    """
    This exception is generated whenever several blocks of the same type are created.
    """
    pass
