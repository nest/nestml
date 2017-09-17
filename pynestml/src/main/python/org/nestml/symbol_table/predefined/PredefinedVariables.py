#
# PredefinedVariables.py
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

class PredefinedVariables:
    """
    This class is used to store all predefined variables as generally available. 
    
    Attributes:
        __E_CONSTANT     The euler constant symbol, i.e. e. Type: str
        __TIME_CONSTANT  The time variable stating the current time since start of simulation. Type: str
    
    """
    __E_CONSTANT = 'e'
    __TIME_CONSTANT = 't'

    @classmethod
    def registerPredefinedVariables(cls, _scope=None):
        """
        Registers the predefined variables in the handed over scope.
        :param _scope: a single, global scope
        :type _scope: Scope
        """
        print('TODO')
        pass