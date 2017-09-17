#
# PredefinedTypes.py
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
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType
from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbolType


class PredefinedTypes:
    """
    This class represents all types which are predefined in the system.
    """

    @classmethod
    def registerPrimitiveTypes(cls, _scope=None):
        """
        Adds a set of primitive data types to the handed over scope. It assures that those types are valid and can
        be used.
        :param _scope: a single scope object. In order to avoid problems, this scope should global.
        :type _scope: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        assert (_scope.getScopeType() == ScopeType.GLOBAL), \
            '(PyNestML.SymbolTable.Predefined) Handed over scope not global!'
        cls.__registerReal(_scope)
        cls.__registerVoid(_scope)
        cls.__registerBoolean(_scope)
        cls.__registerString(_scope)
        cls.__registerInteger(_scope)
        return

    @classmethod
    def __registerReal(cls, _scope=None):
        """
        Adds the real type to the handed over scope.
        :param _scope: a single scope object.
        :type _scope: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        symbol = TypeSymbol(_name='real', _type=TypeSymbolType.PRIMITIVE, _scope=_scope)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerVoid(cls, _scope=None):
        """
        Adds the void type to the handed over scope.
        :param _scope: a single scope object.
        :type _scope: Scope 
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        symbol = TypeSymbol(_name='void', _type=TypeSymbolType.PRIMITIVE, _scope=_scope)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerBoolean(cls, _scope=None):
        """
        Adds the boolean type to the handed over scope.
        :param _scope: a single scope object.
        :type _scope: Scope 
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        symbol = TypeSymbol(_name='boolean', _type=TypeSymbolType.PRIMITIVE, _scope=_scope)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerString(cls, _scope=None):
        """
        Adds the string type to the handed over scope.
        :param _scope: a single scope object.
        :type _scope: Scope 
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        symbol = TypeSymbol(_name='string', _type=TypeSymbolType.PRIMITIVE, _scope=_scope)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerInteger(cls, _scope=None):
        """
        Adds the integer type to the handed over scope.
        :param _scope: a single scope object.
        :type _scope: Scope 
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Predefined) No or wrong type of scope provided!'
        symbol = TypeSymbol(_name='integer', _type=TypeSymbolType.PRIMITIVE, _scope=_scope)
        _scope.addSymbol(symbol)
        return
