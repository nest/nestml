/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTBodyDecorator;
import org.nest.nestml._ast.ASTComponent;
import org.nest.nestml._cocos.NESTMLASTComponentCoCo;

/**
 * Components are not allowed to have dynamics, only neurons are.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class ComponentHasNoDynamics implements NESTMLASTComponentCoCo {


  public static final String ERROR_CODE = "NESTML_COMPONENT_HAS_NO_DYNAMICS";

  public void check(ASTComponent comp) {
    if (comp.getBody() != null) {
      ASTBodyDecorator bodyDecorator = new ASTBodyDecorator(comp.getBody());

      if (!bodyDecorator.getDynamics().isEmpty()) {
        final String msg = "Components do not have dynamics function.";
        error(ERROR_CODE + ":" + msg, comp.get_SourcePositionStart());
      }

    }

  }


}
