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
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class CoCoEachBlockUniqueAndDefined(CoCo):
    """
    This context  condition ensures that each block is defined at most once.
    Not allowed:
        state:
            ...
        end
        ...
        state:
            ...
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks whether each block is define at most once.
        :param _neuron: a single neuron.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BlocksUniques) No or wrong type of neuron provided (%s)!' % type(_neuron)
        if isinstance(_neuron.getStateBlocks(), list) and len(_neuron.getStateBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('State', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that update block is defined exactly once
        if isinstance(_neuron.getUpdateBlocks(), list) and len(_neuron.getUpdateBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Update', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif _neuron.getUpdateBlocks() is None:
            code, message = Messages.getBlockNotDefinedCorrectly('Update', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getUpdateBlocks(), list) and len(_neuron.getUpdateBlocks()) == 0:
            code, message = Messages.getBlockNotDefinedCorrectly('Update', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that parameters block is defined at most once
        if isinstance(_neuron.getParameterBlocks(), list) and len(_neuron.getParameterBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Parameters', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that internals block is defined at most once
        if isinstance(_neuron.getInternalsBlocks(), list) and len(_neuron.getInternalsBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Internals', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that equations block is defined at most once
        if isinstance(_neuron.getEquationsBlocks(), list) and len(_neuron.getEquationsBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Equations', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that input block is defined exactly once
        if isinstance(_neuron.getInputBlocks(), list) and len(_neuron.getInputBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Input', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getInputBlocks(), list) and len(_neuron.getInputBlocks()) == 0:
            code, message = Messages.getBlockNotDefinedCorrectly('Input', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif _neuron.getInputBlocks() is None:
            code, message = Messages.getBlockNotDefinedCorrectly('Input', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        # check that output block is defined exactly once
        if isinstance(_neuron.getOutputBlocks(), list) and len(_neuron.getOutputBlocks()) > 1:
            code, message = Messages.getBlockNotDefinedCorrectly('Output', False)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif isinstance(_neuron.getOutputBlocks(), list) and len(_neuron.getOutputBlocks()) == 0:
            code, message = Messages.getBlockNotDefinedCorrectly('Output', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        elif _neuron.getOutputBlocks() is None:
            code, message = Messages.getBlockNotDefinedCorrectly('Output', True)
            Logger.logMessage(_code=code, _message=message, _neuron=_neuron, _errorPosition=_neuron.getSourcePosition()
                              , _logLevel=LOGGING_LEVEL.ERROR)
        return
