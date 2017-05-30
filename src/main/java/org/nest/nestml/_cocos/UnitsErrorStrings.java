/*
 * UnitsErrorStrings.java
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
package org.nest.nestml._cocos;

import org.nest.nestml._visitor.DotOperatorVisitor;
import org.nest.nestml._visitor.FunctionCallVisitor;
import org.nest.nestml._visitor.ODEPostProcessingVisitor;
import org.nest.nestml._visitor.UnitsSIVisitor;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;

/**
 * Factory for CoCo error strings. The dispatch is done by the static type of the context condition object.
 * IMPORTANT: Error code must start with the SPL_-prefix
 *
 * @author plotnikov, traeder
 */
public class UnitsErrorStrings {
  private static final String SEPARATOR = " : ";

  /**
   * Use static methods to get codes and errors
   */
  private UnitsErrorStrings() {
  }

  public static String expressionCalculation(final ODEPostProcessingVisitor coco, final String description) {
    final String ERROR_MSG_FORMAT = "Error in expression type calculation: " + description;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String expressionNonNumeric(final ODEPostProcessingVisitor coco) {
    final String ERROR_MSG_FORMAT = "Type of LHS Variable in ODE is neither a Unit nor real at.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String expressionMissmatch(
      final ODEPostProcessingVisitor coco,
      final String odeVariable,
      final String odeType,
      final String rhsType) {
    final String ERROR_MSG_FORMAT = "The type of (derived) variable " + odeVariable + " is: " + odeType +
                                    ". This does not match Type of RHS expression: " + rhsType;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final ODEPostProcessingVisitor coco) {
    return "SPL_POST_PROCESSING_ERROR";
  }

  public static String message(final UnitsSIVisitor coco, final String unit) {
    final String ERROR_MSG_FORMAT = "The unit " + unit + " is not a valid SI unit.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final UnitsSIVisitor coco) {
    return "NESTML_SI_VISITOR";
  }

  public static String message(final FunctionCallVisitor coco, final String functionName) {
    final String ERROR_MSG_FORMAT = "Function " + functionName + " with the return-type 'Void'"
                                    + " cannot be used in expressions.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final FunctionCallVisitor coco) {
    return "SPL_FUNCTION_CALL_VISITOR";
  }


  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final DotOperatorVisitor coco) {
    return "SPL_FUNCTION_CALL_VISITOR";
  }
  public static String message(final UnitRepresentation coco, final String representation) {
    final String ERROR_MSG_FORMAT = "Cannot factorize the Unit " + representation;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  public static String code(final UnitRepresentation coco) {
    return "NESTML_UNIT_REPRESENTATION";
  }

}
