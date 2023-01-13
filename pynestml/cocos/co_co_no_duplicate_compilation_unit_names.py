# -*- coding: utf-8 -*-
#
# co_co_no_duplicate_compilation_unit_names.py
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
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


class CoCoNoDuplicateCompilationUnitNames(CoCo):
    """
    This Coco checks that for a handed over list of compilation units, there are not two units that have the same name.
    """

    @classmethod
    def check_co_co(cls, list_of_compilation_units):
        """
        Checks the coco.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        """
        # list_of_nodes = ASTUtils.get_all_nodes(list_of_compilation_units)
        conflicting_nodes = list()
        checked = list()
        for nodeA in list_of_compilation_units:
            for nodeB in list_of_compilation_units:
                if nodeA is not nodeB and nodeA.get_name() == nodeB.get_name():
                    code, message = Messages.get_compilation_unit_name_collision(nodeA.get_name(),
                                                                                 nodeA.get_artifact_name(),
                                                                                 nodeB.get_artifact_name())
                    Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
                conflicting_nodes.append(nodeB)
            checked.append(nodeA)
        return conflicting_nodes
