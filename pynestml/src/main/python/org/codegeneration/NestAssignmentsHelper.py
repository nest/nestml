#
# NestAssignmentsHelper.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.ast.ASTAssignment import ASTAssignment


class NestAssignmentsHelper(object):
    """
    This class contains several helper functions as used during printing of code.
    """

    def lhsVariable(self, _assignment=None):
        """
        Returns the corresponding symbol of the assignment.
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment.
        :return: a single variable symbol
        :rtype: VariableSymbol
        """
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(_assignment)
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName())
        if symbol is not None:
            return symbol
        else:
            Logger.logMessage('No symbol could be resolved!', LOGGING_LEVEL.ERROR)
            return

    def printAssignmentsOperation(self, _assignment=None):
        """
        Returns a nest processable format of the assignment operation.
        :param _assignment: a single assignment
        :type _assignment: ASTAssignment
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(_assignment)
        if _assignment.isCompoundMinus():
            return '+='
        elif _assignment.isCompoundSum():
            return '-='
        elif _assignment.isCompoundProduct():
            return '*='
        elif _assignment.isCompoundQuotient():
            return '/='
        else:
            return '=a'

    def isVectorizedAssignment(self, _assignment=None):
        """
        Indicates whether the handed over assignment is vectorized, i.e., an assignment of vectors.
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        :return: True if vectorized, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(_assignment)
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                        SymbolKind.VARIABLE)
        if symbol is not None:
            if symbol.hasVectorParameter():
                return True
            else:
                # otherwise we have to check if one of the variables used in the rhs is a vector
                for var in _assignment.getExpression().getVariables():
                    symbol = var.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
                    if symbol is not None and symbol.hasVectorParameter():
                        return True
                return False
        else:
            Logger.logMessage('No symbol could be resolved!', LOGGING_LEVEL.ERROR)
            return False

    def printSizeParameter(self, _assignment=None):
        """
        Prints in a nest processable format the size parameter of the assignment.
        :param _assignment: a single assignment
        :type _assignment: ASTAssignment
        :return: the corresponding size parameter
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(_assignment)
        vectorVariable = None
        for variable in _assignment.getExpression().getVaraibles():
            symbol = variable.getScope().resolveToSymbol(variable.getCompleteName(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.hasVectorParameter():
                vectorVariable = symbol
                break
        if vectorVariable is None:
            vectorVariable = _assignment.getScope(). \
                resolveToSymbol(_assignment.getVariable().getCompleteName(), SymbolKind.VARIABLE)
        # this function is called only after the corresponding assignment has been tested for been a vector
        return vectorVariable.getVectorParameter()
