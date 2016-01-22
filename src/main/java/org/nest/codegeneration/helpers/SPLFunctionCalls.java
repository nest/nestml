package org.nest.codegeneration.helpers;

import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTFunctionCall;

/**
 * TODO
 *
 * @author plotnikov
 */
public class SPLFunctionCalls {
  public String printFunctionName(final ASTFunctionCall astFunctionCall) {
    return Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts());
  }

  public boolean isIntegrate(final ASTFunctionCall astFunctionCall) {
    final String functionName = Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts());

    if (functionName.equals("integrate")) {
      return true;
    }
    else {
      return false;
    }

  }

}
