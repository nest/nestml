# -*- coding: utf-8 -*-
#
# error_strings.py
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
from pynestml.utils.ast_source_location import ASTSourceLocation


class ErrorStrings(object):
    """
    These error strings are part of the type calculation system and are kept separated from the message class
    for the sake of a clear and direct maintenance of type system as an individual component.
    """

    SEPARATOR = " : "

    @classmethod
    def code(cls, _origin=None):
        """
        Helper method returning a unique identifier for the various classes that produce and log error messages
        :param _origin: the class reporting an error
        :return: identifier unique to that class
        :rtype: str
        """
        assert _origin is not None
        from pynestml.visitors.ast_unary_visitor import ASTUnaryVisitor
        if isinstance(_origin, ASTUnaryVisitor):
            return "SPL_UNARY_VISITOR"
        from pynestml.visitors.ast_power_visitor import ASTPowerVisitor
        if isinstance(_origin, ASTPowerVisitor):
            return "SPL_POW_VISITOR"
        from pynestml.visitors.ast_logical_not_visitor import ASTLogicalNotVisitor
        if isinstance(_origin, ASTLogicalNotVisitor):
            return "SPL_LOGICAL_NOT_VISITOR"
        from pynestml.visitors.ast_dot_operator_visitor import ASTDotOperatorVisitor
        if isinstance(_origin, ASTDotOperatorVisitor):
            return "SPL_DOT_OPERATOR_VISITOR"
        from pynestml.visitors.ast_line_operation_visitor import ASTLineOperatorVisitor
        if isinstance(_origin, ASTLineOperatorVisitor):
            return "SPL_LINE_OPERATOR_VISITOR"
        from pynestml.visitors.ast_no_semantics_visitor import ASTNoSemanticsVisitor
        if isinstance(_origin, ASTNoSemanticsVisitor):
            return "SPL_NO_SEMANTICS"
        from pynestml.visitors.ast_comparison_operator_visitor import ASTComparisonOperatorVisitor
        if isinstance(_origin, ASTComparisonOperatorVisitor):
            return "SPL_COMPARISON_OPERATOR_VISITOR"
        from pynestml.visitors.ast_binary_logic_visitor import ASTBinaryLogicVisitor
        if isinstance(_origin, ASTBinaryLogicVisitor):
            return "SPL_BINARY_LOGIC_VISITOR"
        from pynestml.visitors.ast_condition_visitor import ASTConditionVisitor
        if isinstance(_origin, ASTConditionVisitor):
            return "SPL_CONDITION_VISITOR"
        from pynestml.visitors.ast_function_call_visitor import ASTFunctionCallVisitor
        if isinstance(_origin, ASTFunctionCallVisitor):
            return "SPL_FUNCTION_CALL_VISITOR"
        return ""

    @classmethod
    def message_non_numeric_type(cls, origin, type_name, source_position):
        """
        construct an error message indicating an expected numeric type is not, in fact, numeric
        :param origin: the class reporting the error
        :param type_name: plain text representation of the wrong type that was encountered
        :type type_name: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot perform an arithmetic operation on a non-numeric type: " + type_name
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_type_error(cls, origin, expression_text, source_position):
        """
        construct an error message indicating a generic error in rhs type calculation
        :param origin: the class reporting the error
        :param expression_text: plain text representation of the offending rhs
        :type expression_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot determine the type of the rhs: " + expression_text
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_implicit_magnitude_conversion(cls, origin, parent_node):
        """
        Construct an warning for implicit conversion from parent_node.rhs to parent_node.lhs
        :param origin: the class dropping the warning
        :param parent_node: the addition,subtraction or assignment that requires implicit conversion
        :type: an ASTExpression that is either an Addition or a Subtraction for which an implicit conversion
        has already been determined
        :return: the warning message
        """

        from pynestml.meta_model.ast_expression import ASTExpression
        from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
        from pynestml.meta_model.ast_assignment import ASTAssignment
        from pynestml.symbols.symbol import SymbolKind
        assert parent_node is not None and (
            isinstance(parent_node, ASTExpression) or isinstance(parent_node, ASTAssignment))

        target_expression = None
        target_unit = None
        convertee_expression = None
        convertee_unit = None
        operation = None

        if isinstance(parent_node, ASTExpression):
            # code duplication from ASTExpressionTypeVisitor:
            # Rules with binary operators
            if parent_node.get_binary_operator() is not None:
                bin_op = parent_node.get_binary_operator()
                # All these rules employ left and right side expressions.
                if parent_node.get_lhs() is not None:
                    target_expression = parent_node.get_lhs()
                    target_unit = target_expression.type.astropy_unit
                if parent_node.get_rhs() is not None:
                    convertee_expression = parent_node.get_rhs()
                    convertee_unit = convertee_expression.type.astropy_unit
                # Handle all Arithmetic Operators:
                if isinstance(bin_op, ASTArithmeticOperator):
                    # Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                    if bin_op.is_plus_op:
                        operation = "+"
                    if bin_op.is_minus_op:
                        operation = "-"

        if isinstance(parent_node, ASTAssignment):
            lhs_variable_symbol = parent_node.get_scope().resolve_to_symbol(
                parent_node.get_variable().get_complete_name(),
                SymbolKind.VARIABLE)
            operation = "="
            target_expression = parent_node.get_variable()
            target_unit = lhs_variable_symbol.get_type_symbol().astropy_unit
            convertee_expression = parent_node.get_expression()
            convertee_unit = convertee_expression.type.astropy_unit

        assert (target_expression is not None and convertee_expression is not None
                and operation is not None), "Only call this on an addition/subtraction  or assignment after " \
                                            "an implicit conversion wrt unit magnitudes has already been determined"

        error_msg_format = "Non-matching unit types at '" + str(parent_node)
        error_msg_format += "'. Implicit conversion of rhs to lhs"
        error_msg_format += " (units: " + str(convertee_unit) + " and " + \
                            str(target_unit) + " )"
        error_msg_format += " implicitly replaced by '" + str(target_expression) + operation \
                            + convertee_expression.printImplicitVersion() + "'"

        return (cls.code(origin) + cls.SEPARATOR + error_msg_format + "("
                + str(parent_node.get_source_position()) + ")")

    @classmethod
    def message_unit_base(cls, origin, source_position):
        """
        construct an error message indicating that a non-int type was given as exponent to a unit type
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "With a Unit base, the exponent must be an integer."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_non_constant_exponent(cls, origin, source_position):
        """
        construct an error message indicating that the exponent given to a unit base is not a constant value
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot calculate value of exponent. Must be a constant value!"
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_expected_bool(cls, origin, source_position):
        """
        construct an error message indicating that an expected bool value was not found
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Expected a bool"
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_expected_int(cls, origin, source_position):
        """
        construct an error message indicating that an expected int value was not found
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Expected an int"
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_add_sub_type_mismatch(cls, origin, lhs_type_text,
                                      rhs_type_text, result_type_text,
                                      source_position):
        """
        construct an message indicating that the types of an addition/subtraction are not compatible
        and that the result is implicitly cast to a different type
        :param origin: the class reporting the error
        :param lhs_type_text: plain text of Lhs type
        :type lhs_type_text: str
        :param rhs_type_text: plain text of Rhs type
        :type rhs_type_text: str
        :param result_type_text: plain text of resulting type (implicit cast)
        :type result_type_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Addition/subtraction of " + lhs_type_text + " and " + rhs_type_text + \
                           ". Assuming: " + result_type_text + "."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_no_semantics(cls, origin, expr_text, source_position):
        """
        construct an error message indicating that an rhs is not implemented
        :param origin: the class reporting the error
        :param expr_text: plain text of the unimplemented rhs
        :type expr_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "This rhs is not implemented: " + expr_text
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_comparison(cls, origin, source_position):
        """
        construct an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Operands of a logical rhs not compatible."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_logic_operands_not_bool(cls, origin, source_position):
        """
        construct an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Both operands of a logical rhs must be boolean."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_ternary(cls, origin, source_position):
        """
        construct an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "The ternary operator condition must be boolean."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_ternary_mismatch(cls, origin, if_true_text, if_not_text, source_position):
        """
        construct an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param if_true_text: plain text of the positive branch of the ternary operator
        :type if_true_text: str
        :param if_not_text: plain text of the negative branch of the ternary operator
        :type if_not_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Mismatched conditional alternatives " + if_true_text + " and " + \
                           if_not_text + "-> Assuming real."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_resolve_fail(cls, origin, symbol_name, source_position):
        """
        construct an error message indicating that a symbol could not be resolved
        :param origin: the class reporting the error
        :param symbol_name: the name of the symbol
        :type symbol_name: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot resolve the symbol: " + symbol_name + "."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_cannot_calculate_convolve_type(cls, origin, source_position):
        """
        construct an error message indicating that the type of a convolve() call is ill-defined
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot calculate return type of convolve()."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"

    @classmethod
    def message_void_function_on_rhs(cls, origin, function_name, source_position):
        """
        construct an error message indicating that a void function cannot be used on a RHS
        :param origin: the class reporting the error
        :param function_name: the offending function
        :type function_name: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Function " + function_name + " with the return-type 'void' cannot be used in expressions."
        return cls.code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
