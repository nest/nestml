# -*- coding: utf-8 -*-
#
# co_co_nest_delay_decorator_specified.py
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
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class CoCoNESTDelayDecoratorSpecified(CoCo):
    """
    This CoCo ensures that there is precisely one parameter decorated as "@nest::delay".
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuronOrSynapse):
        """
        Checks if the coco applies for the node.
        :param node:
        """
        decorator_found = False
        for variable in node.get_parameter_symbols() + node.get_internal_symbols():
            if variable.get_namespace_decorator("nest") == "delay":
                decorator_found = True
                break

        if not decorator_found:
            code, message = Messages.get_nest_delay_decorator_not_found()
            Logger.log_message(node=node, error_position=None,
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
