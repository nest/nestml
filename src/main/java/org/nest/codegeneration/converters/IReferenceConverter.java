/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import org.nest.spl._ast.ASTFunctionCall;
import org.nest.spl._ast.ASTVariable;

public interface IReferenceConverter {

  String  convertBinaryOperator(final String binaryOperator);

  String convertFunctionCall(final ASTFunctionCall astFunctionCall);

  String convertNameReference(final ASTVariable astVariable);

  String convertConstant(final String constantName);

  boolean needsArguments(final ASTFunctionCall astFunctionCall);


}
