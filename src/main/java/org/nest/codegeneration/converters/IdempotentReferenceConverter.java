/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

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
  public String convertFunctionCall(
      final ASTFunctionCall astFunctionCall) {
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

  @Override public boolean needsArguments(ASTFunctionCall astFunctionCall) {
    return astFunctionCall.getArgs().size() > 0;
  }
}
