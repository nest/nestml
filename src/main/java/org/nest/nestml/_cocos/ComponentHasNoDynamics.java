/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTComponent;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Components are not allowed to have dynamics, only neurons are.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class ComponentHasNoDynamics implements NESTMLASTComponentCoCo {


  public static final String ERROR_CODE = "NESTML_COMPONENT_HAS_NO_DYNAMICS";

  public void check(ASTComponent comp) {
    ASTBody bodyDecorator = (comp.getBody());

    if (!bodyDecorator.getDynamics().isEmpty()) {
      NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
      final String msg = errorStrings.getErrorMsg(this);

      error(msg, comp.get_SourcePositionStart());
    }

  }


}
