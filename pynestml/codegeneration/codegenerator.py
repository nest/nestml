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

from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages


class CodeGenerator(object):

    def __init__(self, target):
        assert target in self.get_known_targets()
        self._target = target


    def generate_neurons(self, neurons):
        # type: (list(ASTNeuron)) -> None
        """
        Analyse a list of neurons, solve them and generate the corresponding code.
        :param neurons: a list of neurons.
        """
        from pynestml.frontend.frontend_configuration import FrontendConfiguration

        for neuron in neurons:
            self.generate_neuron_code(neuron)
            if not Logger.has_errors(neuron):
                code, message = Messages.get_code_generated(neuron.get_name(), FrontendConfiguration.get_target_path())
                Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

    @staticmethod
    def get_known_targets():
        return ["NEST", ""]     # include the empty string here to represent "no code generated"


    def generate_code(self, neurons):
        if self._target == "NEST":
            from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
            _codeGenerator = NESTCodeGenerator()
            _codeGenerator.generate_code(neurons)
        elif self._target == "":
            # dummy/null target: user requested to not generate any code
            code, message = Messages.get_no_code_generated()
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
