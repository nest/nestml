"""
/*
 *  CoCoElementDefined.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import SymbolType
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType


class CoCoElementDefined(CoCo):
    """
    This class represents a constraint condition which ensures that all elements as used in expressions have been
    previously defined.
    """

    def checkCoCo(self, _neuron=None):
        """
        Checks if this coco applies for the handed over neuron. Models which use not defined elements are not 
        correct, thus an exception is generated. Caution: This 
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        scope = _neuron.getScope()
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.ElementDefined) No or wrong type of neuron handed over!'
        # first check for the state block, that all used variables and function calls are declared in global scope
        for stateBlock in _neuron.getBody().getStateBlocks():
            for elem in stateBlock.getDeclarations():
                if elem.hasExpression():
                    for var in elem.getExpr().getVariables():
                        # assert that is is defined, but not on the left hand side, thus not e.g., V_m = V_m + 1
                        # assert that the variable is defined in the global scope
                        symbol = scope.resolveToSymbol(var.getName(), SymbolType.VARIABLE)
                        if symbol is None or symbol.getCorrespondingScope().getScopeType() is not ScopeType.GLOBAL or \
                                symbol.getReferencedObject().getSourcePosition().encloses(var.getSourcePosition()):
                            raise ElementNotDefined('Variable ' + var.getName() + ' not defined')
                        else:
                            print('Ok:' + var.getName() + ' defined in ' +
                                  symbol.getReferencedObject().getSourcePosition().printSourcePosition())
                    for fun in elem.getExpr().getFunctions():
                        # assert that the function as used in the update block are defined somewhere
                        symbol = scope.resolveToSymbol(fun.getName(), SymbolType.FUNCTION)
                        # if the corresponding function is not declared, fail
                        if symbol is None:
                            raise ElementNotDefined()

        return


class ElementNotDefined(Exception):
    """
    This exception is thrown whenever an element, which is used in an expression, has not been defined.
    """
    pass
