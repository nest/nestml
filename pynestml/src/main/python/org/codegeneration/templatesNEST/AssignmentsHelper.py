#
# AssignmentsHelper.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL,Logger

class AssignmentsHelper(object):
    """
    This class contains several helper functions as used during printing of code.
    """

    def lhsVariable(self,_assignment = None):
        """
        Returns the corresponding symbol of the assignment.
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment.
        :return: a single variable symbol
        :rtype: VariableSymbol
        """
        from pynestml.src.main.python.org.nestml.ast.ASTAssignment import ASTAssignment
        assert (_assignment is not None and isinstance(_assignment,ASTAssignment)),\
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' %type(_assignment)
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName())
        if symbol is not None:
            return symbol
        else:
            Logger.logMessage('No symbol could be resolved!',LOGGING_LEVEL.ERROR)
            return