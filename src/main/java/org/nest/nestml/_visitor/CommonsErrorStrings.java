/*
 * CommonsErrorStrings.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.nestml._visitor;

import de.se_rwth.commons.SourcePosition;
import org.nest.utils.AstUtils;

/**
 * Factory for CoCo error strings. The dispatch is done by the static type of the context condition object.
 * IMPORTANT: Error code must start with the SPL_-prefix
 *
 * @author plotnikov, traeder
 */
public class CommonsErrorStrings {
  private static final String SEPARATOR = " : ";

  public static String messageType(final DotOperatorVisitor coco,
                                   final String typeMissmatch,
                                   final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = typeMissmatch + "(" + AstUtils.print(sourcePosition) + ")";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String messageModulo(final DotOperatorVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Modulo with non integer parameters.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final DotOperatorVisitor coco) {
    return "SPL_FUNCTION_CALL_VISITOR";
  }

  public static String message(final BinaryLogicVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Both operands of the logical expression must be boolean.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final BinaryLogicVisitor coco) {
    return "SPL_BINARY_LOGIC_VISITOR";
  }

  public static String messageNumeric(final ComparisonOperatorVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Both operands of the logical expression must be boolean.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageComparison(final ComparisonOperatorVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Both operands of the logical expression must be boolean.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final ComparisonOperatorVisitor coco) {
    return "SPL_COMPARISON_OPERATOR_VISITOR";
  }

  public static String messageTernary(final ConditionVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "The ternary operator condition must be boolean.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageTrueNot(final ConditionVisitor coco,
                                      final String ifTrue,
                                      final String ifNot,
                                      final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Mismatched conditional alternatives " + ifTrue + " and " +
                                    ifNot + "-> Assuming real.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageTypeMissmatch(final ConditionVisitor coco,
                                            final String ifTrue,
                                            final String ifNot,
                                            final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Mismatched conditional alternatives " + ifTrue + " and " + ifNot + ".";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final ConditionVisitor coco) {
    return "SPL_CONDITION_VISITOR";
  }

  public static String messageNonNumericType(final UnaryVisitor coco,
                                             final String type,
                                             final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Cannot perform an arithmetic operation on a non-numeric type: " + type;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageTypeError(final UnaryVisitor coco,
                                        final String expression,
                                        final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Cannot determine the type of the expression: " + expression;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final UnaryVisitor coco) {
    return "SPL_UNARY_VISITOR";
  }


  public static String messageDifferentTypes(final LineOperatorVisitor coco,
                                             final String lhsType,
                                             final String rhsType,
                                             final String resultingType,
                                             final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Addition/substraction of " + lhsType + " and " + rhsType +
                                    ". Assuming: " + resultingType + ".";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  public static String messageTypeError(final LineOperatorVisitor coco,
                                        final String lhsType,
                                        final String rhsType,
                                        final String operation,
                                        final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Cannot determine the type of " + operation + " with types: " + lhsType + " and " +
                                    rhsType;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final LineOperatorVisitor coco) {
    return "SPL_LINE_OPERATOR_VISITOR";
  }

  public static String message(final LogicalNotVisitor coco, final String exprType, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Logical 'not' expects an boolean type and not: " + exprType;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final LogicalNotVisitor coco) {
    return "SPL_LOGICAL_NOT_VISITOR";
  }

  public static String message(final NoSemantics coco, final String expr, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "This expression is not implemented: " + expr;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final NoSemantics coco) {
    return "SPL_LOGICAL_NOT_VISITOR";
  }

  public static String messageUnitBase(final PowVisitor coco, final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "With a Unit base, the exponent must be an integer.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageType(final PowVisitor coco,
                                   final String base,
                                   final String exponent,
                                   final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "With a Unit base, the exponent must be an integer.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageFloatingPointExponent(final PowVisitor coco,
                                                    final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "No floating point values allowed in the exponent to a UNIT base";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  public static String messageNonConstantExponent(final PowVisitor coco,
                                                  final SourcePosition sourcePosition) {
    final String ERROR_MSG_FORMAT = "Cannot calculate value of exponent. Must be a constant value!";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT + "(" + AstUtils.print(sourcePosition) + ")";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final PowVisitor coco) {
    return "SPL_POW_VISITOR";
  }

}
