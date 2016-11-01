package org.nest.codegeneration.helpers;

import org.nest.commons._ast.ASTFunctionCall;
import org.nest.symboltable.predefined.PredefinedFunctions;

/**
 * Identifies the predefined function which integrates odes.
 *
 * @author plotnikov
 */
public class SPLFunctionCalls {
  @SuppressWarnings({"unused"}) // used in templates
  public boolean isIntegrate(final ASTFunctionCall astFunctionCall) {
    return astFunctionCall.getCalleeName().equals(PredefinedFunctions.INTEGRATE_ODES);
  }

}
