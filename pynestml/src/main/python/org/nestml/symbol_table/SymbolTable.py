#
# SymbolTable.py
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


class SymbolTable:
    """
    This class is used to store a single symbol table, consisting of scope and symbols.
    
    Attributes:
        __compilationUnitScope       The global (most top) scope of this compilation unit. Type: Scope
    """
    __globalScope = None

    @classmethod
    def initializeSymbolTable(cls, _sourcePosition=None):
        """
        Standard constructor.
        :param _sourcePosition: the source position of the whole compilation unit.
        :type _sourcePosition: ASTSourcePosition
        """
        from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
        assert (_sourcePosition is not None and isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of source position provided!'
        cls.__globalScope = Scope(_scopeType=ScopeType.COMPILATION_UNIT, _sourcePosition=_sourcePosition)
        # initialize all predefined elements
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
        PredefinedTypes.registerPrimitiveTypes()
        PredefinedTypes.registerBufferType()
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import PredefinedFunctions
        PredefinedFunctions.registerPredefinedFunctions()
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedVariables import PredefinedVariables
        PredefinedVariables.registerPredefinedVariables()
        return

    @classmethod
    def addNeuronScope(cls, _scope=None):
        """
        Adds a single neuron scope to the set of stored scopes.
        :return: a single scope element.
        :rtype: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of scope provided!'
        assert (_scope.getScopeType() == ScopeType.GLOBAL), \
            '(PyNestML.SymbolTable.SymbolTable) Only global scopes can be added!'
        if _scope not in cls.__globalScope.getScopes():
            cls.__globalScope.addScope(_scope)
        return

    @classmethod
    def deleteNeuronScope(cls, _scope=None):
        """
        Deletes a single neuron scope from the set of stored scopes.
        :return: a single scope element.
        :rtype: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of scope provided!'
        if _scope in cls.__globalScope.getScopes():
            cls.__globalScope.deleteScope(_scope)
        return

    @classmethod
    def printSymbolTable(cls):
        """
        Prints the content of this symbol table.
        """
        ret = ''
        for scope in cls.__globalScope.getScopes():
            ret += scope.printScope()
        return ret
