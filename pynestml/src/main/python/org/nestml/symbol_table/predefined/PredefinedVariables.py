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
        cls.__registerEulerConstant(_scope)
        cls.__registerTimeConstant(_scope)
        return

    @classmethod
    def __registerEulerConstant(cls, _scope):
        """
        Adds the euler constant e to the handed over scope.    
        :param _scope: a scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import VariableSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        symbol = VariableSymbol(_name='e', _scope=_scope, _blockType=BlockType.STATE,
                                _isPredefined=True, _typeSymbol=TypeSymbol.getRealType())
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerTimeConstant(cls, _scope):
        """
        Adds the time constant t to the handed over scope.    
        :param _scope: a scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import VariableSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.VariableSymbol import BlockType
        print('PredefinedVariables.TODO: Constant t currently real-typed!')
        symbol = VariableSymbol(_name='t', _scope=_scope, _blockType=BlockType.STATE,
                                _isPredefined=True, _typeSymbol=TypeSymbol.getRealType())
        _scope.addSymbol(symbol)
        return
