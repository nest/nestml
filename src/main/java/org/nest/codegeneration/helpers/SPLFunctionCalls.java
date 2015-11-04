package org.nest.codegeneration.helpers;

import de.se_rwth.commons.Names;
import org.nest.spl._ast.ASTFunctionCall;

/**
 * TODO
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since TODO
 */
public class SPLFunctionCalls {
  public String printFunctionName(final ASTFunctionCall astFunctionCall) {
    return Names.getQualifiedName(astFunctionCall.getQualifiedName().getParts());
  }
}
