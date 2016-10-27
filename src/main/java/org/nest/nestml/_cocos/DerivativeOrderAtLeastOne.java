/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._cocos.ODEASTEquationCoCo;

/**
 * Syntactically it is possible to define an equation:
 * equations:
 *   V_m = I_syn # not V_m'
 * end
 *
 * @author plotnikov
 */
public class DerivativeOrderAtLeastOne implements ODEASTEquationCoCo {
  public static final String ERROR_CODE = "NESTML_DERIVATIVE_ORDER_AT_LEAST_ONE";
  private final NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();

  @Override
  public void check(final ASTEquation astEq) {
    if (astEq.getLhs().getDifferentialOrder().size() == 0) {
      Log.error(errorStrings.getErrorMsg(this, astEq.getLhs().toString()), astEq.get_SourcePositionStart());
    }

  }


}
