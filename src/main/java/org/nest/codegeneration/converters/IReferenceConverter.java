/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;

/**
 * Defines which names can be mapped.
 *
 * @author plotnikov
 */
public interface IReferenceConverter {

  String convertBinaryOperator(final String binaryOperator);

  String convertFunctionCall(final ASTFunctionCall astFunctionCall);

  String convertNameReference(final ASTVariable astVariable);

  String convertConstant(final String constantName);

  default boolean needsArguments(ASTFunctionCall astFunctionCall) {
    return astFunctionCall.getArgs().size() > 0;
  }

}
