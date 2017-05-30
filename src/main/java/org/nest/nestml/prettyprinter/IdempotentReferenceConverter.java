/*
 * IdempotentReferenceConverter.java
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
package org.nest.nestml.prettyprinter;

import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;

/**
 * Returns the same input as output.
 *
 * @author plotnikov
 */
public class IdempotentReferenceConverter implements IReferenceConverter {

  @Override
  public String convertBinaryOperator(String binaryOperator) {
    return "(%s)" + binaryOperator + "(%s)";
  }

  @Override
  public String convertFunctionCall(final ASTFunctionCall astFunctionCall) {
    final StringBuilder result = new StringBuilder();
    result.append(astFunctionCall.getCalleeName());

    if (needsArguments(astFunctionCall)) {
      result.append("(%s)");
    }
    else {
      result.append("()");
    }

    return result.toString();
  }

  @Override
  public String convertNameReference(final ASTVariable astVariable) {
    return astVariable.toString();
  }

  @Override
  public String convertConstant(final String constantName) {
    return constantName;
  }

}
