#
# NestNamesConverter.py
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
from pynestml.modelprocessor.VariableSymbol import VariableSymbol


class NestNamesConverter(object):
    """
    This class provides several methods which can be used to convert names of objects to the corresponding
    nest representation.
    """

    @classmethod
    def name(cls, _obj=None):
        """
        Returns for the handed over element the corresponding nest processable string.
        :param _obj: a single variable symbol or variable
        :type _obj: VariableSymbol or ASTVariable
        :return: the corresponding string representation
        :rtype: str
        """
        if isinstance(_obj, VariableSymbol):
            return cls.convertToCPPName(_obj.getSymbolName())
        else:
            return cls.convertToCPPName(_obj.getCompleteName())

    @classmethod
    def getter(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the getter to a nest processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return 'get_' + cls.convertToCPPName(_variableSymbol.getSymbolName())

    @classmethod
    def bufferValue(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return _variableSymbol.getSymbolName() + '_grid_sum_'

    @classmethod
    def setter(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the setter to a nest processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return 'set_' + cls.convertToCPPName(_variableSymbol.getSymbolName())

    @classmethod
    def convertToCPPName(cls, _variableName=None):
        """
        Converts a handed over name to the corresponding nest / c++ naming guideline.
        In concrete terms:
            Converts names of the form g_in'' to a compilable C++ identifier: __DDX_g_in
        :param _variableName: a single name.
        :type _variableName: str
        :return: the corresponding transformed name.
        :rtype: str
        """
        differentialOrder = _variableName.count('\'')
        if differentialOrder > 0:
            return '__' + 'D' * differentialOrder + '_' + _variableName.replace('\'', '')
        else:
            return _variableName
