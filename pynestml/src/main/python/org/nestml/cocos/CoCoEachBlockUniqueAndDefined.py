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
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class CoCoEachBlockUniqueAndDefined(CoCo):
    """
    This context  condition ensures that each block is defined at most once.
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks whether each block is define at most once.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.ElementDefined) No or wrong type of neuron provided (%s)!' % type(_neuron)
        if isinstance(_neuron.getStateBlocks(), list) and len(_neuron.getStateBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] State block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that update block is defined exactly once
        if isinstance(_neuron.getUpdateBlocks(), list) and len(_neuron.getUpdateBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Update block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif _neuron.getUpdateBlocks() is None:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Update block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getUpdateBlocks(), list) and len(_neuron.getUpdateBlocks()) == 0:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Update block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that parameters block is defined at most once
        if isinstance(_neuron.getParameterBlocks(), list) and len(_neuron.getParameterBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Parameters block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that internals block is defined at most once
        if isinstance(_neuron.getInternalsBlocks(), list) and len(_neuron.getInternalsBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Internals block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that equations block is defined at most once
        if isinstance(_neuron.getEquationsBlocks(), list) and len(_neuron.getEquationsBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Equations block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that input block is defined exactly once
        if isinstance(_neuron.getInputBlocks(), list) and len(_neuron.getInputBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Input block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getInputBlocks(), list) and len(_neuron.getInputBlocks()) == 0:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Input block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif _neuron.getInputBlocks() is None:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Input block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        # check that output block is defined exactly once
        if isinstance(_neuron.getOutputBlocks(), list) and len(_neuron.getOutputBlocks()) > 1:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Output block not unique, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getOutputBlocks(), list) and len(_neuron.getOutputBlocks()) == 0:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Output block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        elif _neuron.getOutputBlocks() is None:
            Logger.logMessage('[' + _neuron.getName() + '.nestml] Output block not defined, model not correct!',
                              LOGGING_LEVEL.ERROR)
        return
