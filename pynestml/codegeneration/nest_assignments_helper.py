# -*- coding: utf-8 -*-
#
# nest_assignments_helper.py
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

from typing import Optional

from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.logger import LoggingLevel, Logger


class NestAssignmentsHelper:
    """
    This class contains several helper functions as used during printing of code.
    """

    @classmethod
    def lhs_variable(cls, assignment: ASTAssignment) -> Optional[VariableSymbol]:
        """
        Returns the corresponding symbol of the assignment.
        :param assignment: a single assignment.
        :return: a single variable symbol
        """
        assert isinstance(assignment, ASTAssignment), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(assignment)
        symbol = assignment.get_scope().resolve_to_symbol(assignment.get_variable().get_complete_name(),
                                                          SymbolKind.VARIABLE)
        if symbol is not None:
            return symbol

        Logger.log_message(message='No symbol could be resolved!', log_level=LoggingLevel.ERROR)
        return None

    @classmethod
    def lhs_vector_variable(cls, assignment: ASTAssignment) -> VariableSymbol:
        """
        Returns the corresponding symbol of the assignment.
        :param assignment: a single assignment.
        :return: a single variable symbol
        """
        assert isinstance(assignment, ASTAssignment), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(assignment)
        symbol = assignment.get_scope().resolve_to_symbol(assignment.get_variable().get_vector_parameter(),
                                                          SymbolKind.VARIABLE)
        if symbol is not None:
            return symbol

        Logger.log_message(message='No symbol could be resolved!', log_level=LoggingLevel.WARNING)
        return None

    @classmethod
    def print_assignments_operation(cls, assignment) -> str:
        """
        Returns a nest processable format of the assignment operation.
        :param assignment: a single assignment
        :type assignment: ASTAssignment
        :return: the corresponding string representation
        """
        assert isinstance(assignment, ASTAssignment), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(assignment)
        if assignment.is_compound_sum:
            return '+='

        if assignment.is_compound_minus:
            return '-='

        if assignment.is_compound_product:
            return '*='

        if assignment.is_compound_quotient:
            return '/='

        return '='

    @classmethod
    def is_vectorized_assignment(cls, assignment) -> bool:
        """
        Indicates whether the handed over assignment is vectorized, i.e., an assignment of vectors.
        :param assignment: a single assignment.
        :type assignment: ASTAssignment
        :return: True if vectorized, otherwise False.
        """
        from pynestml.symbols.symbol import SymbolKind
        assert isinstance(assignment, ASTAssignment), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(assignment)
        symbol = assignment.get_scope().resolve_to_symbol(assignment.get_variable().get_complete_name(),
                                                          SymbolKind.VARIABLE)
        if symbol is not None:
            if symbol.has_vector_parameter():
                return True

            # otherwise we have to check if one of the variables used in the rhs is a vector
            for var in assignment.get_expression().get_variables():
                symbol = var.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
                if symbol is not None and symbol.has_vector_parameter():
                    return True

            return False

        Logger.log_message(message='No symbol could be resolved!', log_level=LoggingLevel.ERROR)
        return False

    @classmethod
    def print_size_parameter(cls, assignment) -> str:
        """
        Prints in a nest processable format the size parameter of the assignment.
        :param assignment: a single assignment
        :type assignment: ASTAssignment
        :return: the corresponding size parameter
        """
        from pynestml.symbols.symbol import SymbolKind
        assert (assignment is not None and isinstance(assignment, ASTAssignment)), \
            '(PyNestML.CodeGeneration.Assignments) No or wrong type of assignment provided (%s)!' % type(assignment)
        vector_variable = None
        for variable in assignment.get_expression().get_variables():
            symbol = variable.get_scope().resolve_to_symbol(variable.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.has_vector_parameter():
                vector_variable = symbol
                break
        if vector_variable is None:
            vector_variable = assignment.get_scope(). \
                resolve_to_symbol(assignment.get_variable().get_complete_name(), SymbolKind.VARIABLE)
        # this function is called only after the corresponding assignment has been tested for been a vector
        return vector_variable.get_vector_parameter()
