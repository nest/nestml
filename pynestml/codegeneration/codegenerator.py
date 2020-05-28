#
# codegeneration.py
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

from typing import List

from pynestml.exceptions.invalid_target_exception import InvalidTargetException
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages


class CodeGenerator():

    def __init__(self, target):
        if not target.upper() in self.get_known_targets():
            code, msg = Messages.get_unknown_target(target)
            Logger.log_message(message=msg, code=code, log_level=LoggingLevel.ERROR)
            self._target = ""
            raise InvalidTargetException()

        self._target = target

    @staticmethod
    def get_known_targets():
        targets = ["NEST", "autodoc", ""]     # include the empty string here to represent "no code generated"
        targets = [s.upper() for s in targets]
        return targets

    def generate_neurons(self, neurons: List[ASTNode]):
        """
        Generate code for the given neurons.

        :param neurons: a list of neurons.
        :type neurons: List[ASTNode]
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for neuron in neurons:
            self.generate_neuron_code(neuron)
            if not Logger.has_errors(neuron):
                code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
                Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

    def generate_code(self, neurons):
        """
        Generate code for the given neurons and (depending on the target) generate an index page, module entrypoint or
        similar that incorporates an enumeration of all neurons.

        :param neurons: a list of neurons.
        :type neurons: List[ASTNode]
        """
        if self._target.upper() == "NEST":
            from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
            _codeGenerator = NESTCodeGenerator()
            _codeGenerator.generate_code(neurons)
        elif self._target.upper() == "AUTODOC":
            from pynestml.codegeneration.autodoc_codegenerator import AutoDocCodeGenerator
            _codeGenerator = AutoDocCodeGenerator()
            _codeGenerator.generate_code(neurons)
        else:
            # dummy/null target: user requested to not generate any code
            assert self._target == ""
            code, message = Messages.get_no_code_generated()
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
