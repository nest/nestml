#
# ASTUtils.py
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


class ASTUtils(object):
    """
    A collection of helpful methods.
    """

    @classmethod
    def getAllNeurons(cls, _listOfCompilationUnits=list()):
        """
        For a list of compilation units, it returns a list containing all neurons defined in all compilation
        units.
        :param _listOfCompilationUnits: a list of compilation units.
        :type _listOfCompilationUnits: list(ASTNESTMLCompilationUnit)
        :return: a list of neurons
        :rtype: list(ASTNeuron)
        """
        ret = list()
        for compiunit in _listOfCompilationUnits:
            ret.extend(compiunit.getNeuronList())
        return ret
