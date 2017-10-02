#
# NestFunctions.py
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
from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall


class NestFunctions(object):
    """
    This class contains several methods as used during the generation of nest code.
    """

    @classmethod
    def isIntegration(cls, _ast):
        """
        Indicates whether the handed over ast represents a ode integration function call.
        :param _ast: a single ast function call.
        :type _ast: ASTFunctionCall
        :return: True if integration, otherwise False.
        :rtype: bool
        """
        # TODO
        return isinstance(_ast, ASTFunctionCall) and _ast.getName() == 'integrate_odes'
