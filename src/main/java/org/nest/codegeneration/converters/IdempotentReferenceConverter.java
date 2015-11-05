/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTFunctionCall;

/**
 * Returns the same input as output.
 *
 * @author plotnikov
 */
public class IdempotentReferenceConverter implements IReferenceConverter {

  @Override
  public String convertFunctionCall(
      final ASTFunctionCall astFunctionCall) {
    final StringBuilder result = new StringBuilder();
    result.append(Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts()));

    if (needsArguments(astFunctionCall)) {
      result.append("(%s)");
    }
    else {
      result.append("()");
    }
    return result.toString();
  }

  @Override
  public String convertNameReference(final ASTQualifiedName astQualifiedName) {
    return Names.getQualifiedName(astQualifiedName.getParts());
  }

  @Override
  public String convertConstant(final String constantName) {
    return constantName;
  }

  @Override public boolean needsArguments(ASTFunctionCall astFunctionCall) {
    return astFunctionCall.getArgList().getArgs().size() > 0;
  }
}
