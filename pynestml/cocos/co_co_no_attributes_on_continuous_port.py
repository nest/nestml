# -*- coding: utf-8 -*-
#
# co_co_no_attributes_on_continuous_port.py
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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class CoCoNoAttributesOnContinuousPort(CoCo):
    """
    This context condition checker ensures that no attributes are defined on continuous time output ports.
    """

    @classmethod
    def check_co_co(cls, neuron: ASTModel):
        """
        Checks the coco for the handed over neuron.
        :param neuron: a single neuron instance.
        """
        output_blocks = neuron.get_output_blocks()
        if not len(output_blocks) == 1:
            # too few or too many output blocks; this will be checked elsewhere
            return

        output_block = output_blocks[0]

        if output_block.is_continuous() and output_block.get_attributes():
            code, message = Messages.get_continuous_output_port_cannot_have_attributes()
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                               error_position=output_block.get_source_position())
            return
