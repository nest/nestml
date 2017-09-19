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
from copy import copy


class PredefinedVariables:
    """
    This class is used to store all predefined variables as generally available. 
    
    Attributes:
        __E_CONSTANT     The euler constant symbol, i.e. e. Type: str
        __TIME_CONSTANT  The time variable stating the current time since start of simulation. Type: str
        __name2VariableSymbol A list of all currently defined variables. Type: list(VariableSymbol)
    
    """
    __name2VariableSymbol = {}  # a map from names to symbols

    __E_CONSTANT = 'e'
    __TIME_CONSTANT = 't'

    @classmethod
    def registerPredefinedVariables(cls):
        """
        Registers the predefined variables.
        """
        # TODO: Registration of units.
        cls.__registerEulerConstant()
        cls.__registerTimeConstant()
        return

    @classmethod
    def __registerEulerConstant(cls):
        """
        Adds the euler constant e.
        """
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import VariableSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbol = VariableSymbol(_name='e', _blockType=BlockType.STATE,
                                _isPredefined=True, _typeSymbol=PredefinedTypes.getRealType())
        cls.__name2VariableSymbol[cls.__E_CONSTANT] = symbol
        return

    @classmethod
    def __registerTimeConstant(cls):
        """
        Adds the time constant t.
        """
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import VariableSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        print('PredefinedVariables.TODO: Constant t currently real-typed!')
        symbol = VariableSymbol(_name='t', _blockType=BlockType.STATE,
                                _isPredefined=True, _typeSymbol=PredefinedTypes.getRealType())
        cls.__name2VariableSymbol[cls.__TIME_CONSTANT] = symbol
        return

    @classmethod
    def getTimeConstant(cls):
        """
        Returns a copy of the variable symbol representing the time constant t.    
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return copy(cls.__name2VariableSymbol[cls.__TIME_CONSTANT])

    @classmethod
    def getEulerConstant(cls):
        """
        Returns a copy of the variable symbol representing the euler constant t.    
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return copy(cls.__name2VariableSymbol[cls.__E_CONSTANT])

    @classmethod
    def getVariableIfExists(cls, _name=None):
        """
        Returns the variable symbol belonging to the handed over name if such an element exists.
        :param _name: the name of a symbol.
        :type _name: str
        :return: a variable symbol if one exists, otherwise none
        :rtype: None or VariableSymbol
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.PredefinedVariables) No or wrong type of name provided!'
        if _name in cls.__name2VariableSymbol.keys():
            return copy(cls.__name2VariableSymbol[_name])
        else:
            return None

    @classmethod
    def getVariables(cls):
        """
        Returns the list of all defined variables.
        :return: a list of variable symbols.
        :rtype: list(VariableSymbol)
        """
        return copy(cls.__name2VariableSymbol)
