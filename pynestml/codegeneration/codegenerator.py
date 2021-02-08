# -*- coding: utf-8 -*-
#
# codegenerator.py
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
from typing import Any, Mapping, Optional, Sequence

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages


class CodeGenerator:

    _default_options: Mapping[str, Any] = {}

    def __init__(self, target, options: Optional[Mapping[str, Any]]=None):
        if not target.upper() in self.get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            raise InvalidTargetException()

        self._target = target
        if "_default_options" in dir(self.__class__):
            self._options = dict(self.__class__._default_options)
        if options:
            self.set_options(options)

    def generate_code(self, neurons) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def generate_neuron_code(self, neuron) -> None:
        """the base class CodeGenerator does not generate any code"""
        pass

    def set_options(self, options: Mapping[str, Any]):
        if not "_default_options" in dir(self.__class__):
            assert "Code generator class \"" + str(self.__class__) + "\" does not support setting options."
        for k in options.keys():
            assert k in self.__class__._default_options, "Option \"" + str(k) + "\" does not exist in code generator"
        self._options.update(options)

    def get_option(self, k):
        return self._options[k]

    def generate_neurons(self, neurons: Sequence[ASTNeuron]):
        """
        Generate code for the given neurons.

        :param neurons: a list of neurons.
        :type neurons: Sequence[ASTNeuron]
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for neuron in neurons:
            self.generate_neuron_code(neuron)
            if not Logger.has_errors(neuron):
                code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
                Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

    @staticmethod
    def get_known_targets():
        targets = ["NEST", "autodoc", ""]     # include the empty string here to represent "no code generated"
        targets = [s.upper() for s in targets]
        return targets

    @staticmethod
    def from_target_name(target_name: str, options: Optional[Mapping[str, Any]]=None) -> CodeGenerator:
        """Static factory method that returns a new instance of a child class of CodeGenerator"""
        assert target_name.upper() in CodeGenerator.get_known_targets(), "Unknown target platform requested: \"" + str(target_name) + "\""
        if target_name.upper() == "NEST":
            from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
            return NESTCodeGenerator(options)
        elif target_name.upper() == "AUTODOC":
            from pynestml.codegeneration.autodoc_codegenerator import AutoDocCodeGenerator
            assert options is None or options == {}, "\"autodoc\" code generator does not support options"
            return AutoDocCodeGenerator()
        elif target_name == "":
            # dummy/null target: user requested to not generate any code
            code, message = Messages.get_no_code_generated()
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
            return CodeGenerator("", options)
        assert False  # cannot reach here due to earlier assert -- silence static checker warnings
