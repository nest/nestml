"""
/*
 *  SymbolTableASTVisitor.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import Symbol
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.ast.ASTVar_Block import ASTVar_Block
from pynestml.src.main.python.org.nestml.ast.ASTDynamics import ASTDynamics
from pynestml.src.main.python.org.nestml.ast.ASTFunction import ASTFunction
from pynestml.src.main.python.org.nestml.ast.ASTBlock import ASTBlock


class SymbolTableASTVisitor:
    """
    This class is used to create a symbol table from a handed over AST.
    """

    @classmethod
    def createSymbolTable(cls, _ast=None):
        """
        Creates for the handed over ast the corresponding symbol table.
        :param _ast: a AST neuron object as used to create the symbol table
        :type _ast: ASTNeuron
        :return: a new symbol table
        :rtype: SymbolTable
        """
        assert (_ast is not None and isinstance(_ast, ASTNeuron)), \
            '(PyNestML.SymbolTable.Visitor) Not a neuron instance handed over!'
        return SymbolTableASTVisitor.__visitNeuron(_ast)

    @classmethod
    def __visitNeuron(cls, _neuron=None):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: 
        :rtype: 
        """
        scope = Scope(_scopeType=ScopeType.GLOBAL, _sourcePosition=_neuron.getSourcePosition())
        # first, create foll all elements as defined in the var blocks the corresponding GLOBAL symbols
        for bodyElement in _neuron.getBody():
            if isinstance(bodyElement, ASTVar_Block):
                for decl in bodyElement.getDeclarations():
                    scope.addSymbolToScope(Symbol(_sourcePosition=decl.getSourcePosition(), _elementReference=decl))
            if isinstance(bodyElement, ASTDynamics):
                scope.addScopeToScope(SymbolTableASTVisitor.__visitUpdateBlock(bodyElement))
            if isinstance(bodyElement, ASTFunction):
                scope.addScopeToScope(SymbolTableASTVisitor.__visitFunctionBlock(bodyElement))
        return scope

    @classmethod
    def __visitFunctionBlock(cls, _block=None):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param _block: a function block object.
        :type _block: ASTFunction
        :return: a new scope object.
        :rtype: Scope
        """
        assert (_block is not None and isinstance(_block, ASTFunction)), \
            '(PyNestML.SymbolTable.Visitor) Not a function block!'
        scope = Scope(_scopeType=ScopeType.FUNCTION, _sourcePosition=_block.getSourcePosition())
        for arg in _block.getParameters().getParametersList():
            scope.addSymbolToScope(Symbol(_sourcePosition=arg.getSourcePosition(), _elementReference=arg))
        for elem in _block.getBlock().getStmts():
            pass
        return scope

    @classmethod
    def __visitUpdateBlock(cls, _block=None):
        """
        Private method: Used to visit a single update block and create the corresponding scope.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        :return: a new scope object.
        :rtype: Scope
        """
        assert (_block is not None and isinstance(_block, ASTDynamics)), \
            '(PyNestML.SymbolTable.Visitor) Not an update block!'
        scope = Scope(_scopeType=ScopeType.UPDATE, _sourcePosition=_block.getSourcePosition())
        for elem in _block.getBlock():
            if elem.isSmallStmt():
                pass
            else:
                scope.addScopeToScope(SymbolTableASTVisitor.__visitSubBlock())
        return scope

    @classmethod
    def __visitSubBlock(cls, _block=None):
        """
        Private method: Used to visit a single sub-block (e.g. if-block) and create the corresponding scope.
        :param _block: a sub-block.
        :type _block: ASTBlock
        :return: a new scope object.
        :rtype: Scope
        """
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.SymbolTable.Visitor) Not a block handed over!'
        scope = Scope(_scopeType=ScopeType.LOCAL, _sourcePosition=_block.getSourcePosition())
        for elem in _block.getStmts():
            pass
        return scope
