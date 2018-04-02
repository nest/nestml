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
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType, VariableType


class PredefinedVariables(object):
    """
    This class is used to store all predefined variables as generally available. 
    
    Attributes:
        E_CONSTANT (str): The euler constant symbol, i.e. e. Type: str
        TIME_CONSTANT (str):  The time variable stating the current time since start of simulation. Type: str
        __name2variable (dict): A map from variable names to their respective symbols.
    """
    __name2variable = {}  # a map from names to symbols
    E_CONSTANT = 'e'
    TIME_CONSTANT = 't'

    @classmethod
    def registerPredefinedVariables(cls):
        """
        Registers the predefined variables.
        """
        cls.__name2variable = {}
        cls.__registerEulerConstant()
        cls.__registerTimeConstant()
        cls.__registerPredefinedTypeVariables()
        return

    @classmethod
    def __registerPredefinedTypeVariables(cls):
        """
        Registers all predefined type variables, e.g., mV and integer.
        """
        for name in PredefinedTypes.getTypes().keys():
            symbol = VariableSymbol(name=name, block_type=BlockType.PREDEFINED,
                                    is_predefined=True,
                                    type_symbol=PredefinedTypes.getTypeIfExists(name),
                                    variable_type=VariableType.VARIABLE)
            cls.__name2variable[name] = symbol
        return

    @classmethod
    def __registerEulerConstant(cls):
        """
        Adds the euler constant e.
        """
        symbol = VariableSymbol(name='e', block_type=BlockType.STATE,
                                is_predefined=True, type_symbol=PredefinedTypes.getRealType(),
                                variable_type=VariableType.VARIABLE)
        cls.__name2variable[cls.E_CONSTANT] = symbol
        return

    @classmethod
    def __registerTimeConstant(cls):
        """
        Adds the time constant t.
        """
        symbol = VariableSymbol(name='t', block_type=BlockType.STATE,
                                is_predefined=True, type_symbol=PredefinedTypes.getTypeIfExists('ms'),
                                variable_type=VariableType.VARIABLE)
        cls.__name2variable[cls.TIME_CONSTANT] = symbol
        return

    @classmethod
    def getTimeConstant(cls):
        """
        Returns a copy of the variable symbol representing the time constant t.    
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return cls.__name2variable[cls.TIME_CONSTANT]

    @classmethod
    def getEulerConstant(cls):
        """
        Returns a copy of the variable symbol representing the euler constant t.    
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return cls.__name2variable[cls.E_CONSTANT]

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
            '(PyNestML.SymbolTable.PredefinedVariables) No or wrong type of name provided (%s)!' % type(_name)
        if _name in cls.__name2variable.keys():
            return cls.__name2variable[_name]
        else:
            return None

    @classmethod
    def getVariables(cls):
        """
        Returns the list of all defined variables.
        :return: a list of variable symbols.
        :rtype: list(VariableSymbol)
        """
        return cls.__name2variable
