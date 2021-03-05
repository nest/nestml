# -*- coding: utf-8 -*-
#
# co_co_state_variables_initialized.py
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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class CoCoStateVariablesInitialized(CoCo):
    """
    This CoCo ensures that all the variables declared in the state block are initialized with a value.
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        """
        Checks if the coco applies for the node. All the variables declared in the state block
        must be initialized with a value.
        :param node:
        """
        for variable in node.get_state_symbols():
            if not variable.has_declaring_expression():
                code, message = Messages.get_state_variables_not_initialized(var_name=variable.get_symbol_name())
                Logger.log_message(error_position=node.get_source_position(),
                                   code=code, message=message,
                                   log_level=LoggingLevel.ERROR)
