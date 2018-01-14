#
# GSLNamesConverter.py
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
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter


class GSLNamesConverter(object):
    """
    A GSL names converter as use to transform names to GNU Scientific Library.
    """

    @classmethod
    def arrayIndex(cls, _symbol=None):
        """
        Transforms the haded over symbol to a GSL processable format.
        :param _symbol: a single variable symbol
        :type _symbol: VariableSymbol
        :return: the corresponding string format
        :rtype: str
        """
        assert (_symbol is not None and isinstance(_symbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.GSLNamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _symbol)
        return 'State_::' + NestNamesConverter.convertToCPPName(_symbol.getSymbolName())

    @classmethod
    def name(cls, _symbol=None):
        """
        Transforms the haded over symbol to a GSL processable format.
        :param _symbol: a single variable symbol
        :type _symbol: VariableSymbol
        :return: the corresponding string format
        :rtype: str
        """
        assert (_symbol is not None and isinstance(_symbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.GSLNamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _symbol)
        if _symbol.isInitValues() and not _symbol.isFunction():
            return 'ode_state[State_::' + NestNamesConverter.convertToCPPName(_symbol.getSymbolName()) + ']'
        else:
            return NestNamesConverter.name(_symbol)

    @classmethod
    def getter(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the getter to a gsl processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return NestNamesConverter.getter(_variableSymbol)

    @classmethod
    def setter(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the setter to a gsl processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return NestNamesConverter.setter(_variableSymbol)

    @classmethod
    def bufferValue(cls, _variableSymbol=None):
        """
        Converts for a handed over symbol the corresponding name of the buffer to a gsl processable format.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        return NestNamesConverter.bufferValue(_variableSymbol)

    @classmethod
    def convertToCPPName(cls, _variableName=None):
        """
        Converts a handed over name to the corresponding gsl / c++ naming guideline.
        In concrete terms:
            Converts names of the form g_in'' to a compilable C++ identifier: __DDX_g_in
        :param _variableName: a single name.
        :type _variableName: str
        :return: the corresponding transformed name.
        :rtype: str
        """
        return NestNamesConverter.convertToCPPName(_variableName)
