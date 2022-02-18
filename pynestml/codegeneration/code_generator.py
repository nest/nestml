# -*- coding: utf-8 -*-
#
# code_generator.py
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

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence

import copy

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.with_options import WithOptions


class CodeGenerator(WithOptions):

    _default_options: Mapping[str, Any] = {}

    def __init__(self, target, options: Optional[Mapping[str, Any]] = None):
        super(CodeGenerator, self).__init__(options)
        from pynestml.frontend.pynestml_frontend import get_known_targets

        if not target.upper() in get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target
        self.is_transformed = False

    def generate_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def transform(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def generate_neurons(self, neurons: Sequence[ASTNeuron]) -> None:
        """
        Generate code for the given neurons.

        :param neurons: a list of neurons.
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for neuron in neurons:
            self.generate_neuron_code(neuron)
            if not Logger.has_errors(neuron):
                code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
                Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

    def generate_synapses(self, synapses: Sequence[ASTSynapse]) -> None:
        """
        Generates code for a list of synapses.
        :param synapses: a list of synapses.
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for synapse in synapses:
            if Logger.logging_level == LoggingLevel.INFO:
                print("Generating code for the synapse {}.".format(synapse.get_name()))
            self.generate_synapse_code(synapse)
            code, message = Messages.get_code_generated(synapse.get_name(), FrontendConfiguration.get_target_path())
            Logger.log_message(synapse, code, message, synapse.get_source_position(), LoggingLevel.INFO)
