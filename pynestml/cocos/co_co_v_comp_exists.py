# -*- coding: utf-8 -*-
#
# co_co_v_comp_exists.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.messages import Messages
from pynestml.utils.logger import Logger, LoggingLevel


class CoCoVCompDefined(CoCo):
    """
    This class represents a constraint condition which ensures that variable v_comp has been
    defined if we have compartmental model case.
    When we start code generation with NEST_COMPARTMENTAL flag the following must exist:
        state:
            v_comp real = 0
    """

    @classmethod
    def check_co_co(cls, neuron: ASTNeuron):
        """
        Checks if this coco applies for the handed over neuron.
        Models which are supposed to be compartmental but do not contain
        state variable called v_comp are not correct.
        :param neuron: a single neuron instance.
        :param after_ast_rewrite: indicates whether this coco is checked
            after the code generator has done rewriting of the abstract syntax tree.
            If True, checks are not as rigorous. Use False where possible.
        """
        from pynestml.codegeneration.nest_compartmental_code_generator import NESTCompartmentalCodeGenerator

        if not FrontendConfiguration.get_target_platform().upper() == 'NEST_COMPARTMENTAL':
            return

        enforced_variable_name = NESTCompartmentalCodeGenerator._default_options["compartmental_variable_name"]

        state_blocks = neuron.get_state_blocks()
        if state_blocks is None:
            cls.log_error(neuron, neuron.get_source_position(), enforced_variable_name)
            return False

        if isinstance(state_blocks, ASTBlockWithVariables):
            state_blocks = [state_blocks]

        for state_block in state_blocks:
            declarations = state_block.get_declarations()
            for declaration in declarations:
                variables = declaration.get_variables()
                for variable in variables:
                    variable_name = variable.get_name().lower().strip()
                    if variable_name == enforced_variable_name:
                        return True

        cls.log_error(neuron, state_blocks[0].get_source_position(), enforced_variable_name)
        return False

    @classmethod
    def log_error(cls, neuron: ASTNeuron, error_position, missing_variable_name):
        code, message = Messages.get_v_comp_variable_value_missing(neuron.get_name(), missing_variable_name)
        Logger.log_message(error_position=error_position, node=neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
