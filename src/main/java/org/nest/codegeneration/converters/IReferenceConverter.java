/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.converters;

import de.monticore.types.types._ast.ASTQualifiedName;
import org.nest.spl._ast.ASTFunctionCall;

public interface IReferenceConverter {

  String convertFunctionCall(final ASTFunctionCall astFunctionCall);

  String convertNameReference(final ASTQualifiedName astQualifiedName);

  String convertConstant(final String constantName);

  boolean needsArguments(final ASTFunctionCall astFunctionCall);

}
