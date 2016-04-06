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
 * Components are not allowed to have inputs, only neurons are.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class ComponentNoInput implements NESTMLASTComponentCoCo {

  public static final String ERROR_CODE = "NESTML_COMPONENT_NO_INPUT";

  @Override
  public void check(ASTComponent comp) {
    ASTBody bodyDecorator = comp.getBody();

    if (bodyDecorator.getInputLines() != null) { // TODO null check makes no sense
      if (!bodyDecorator.getInputLines().isEmpty()) {
        final String msg = "Components cannot have inputs, since they are not elements of a "
            + "neuronal network.";
       error(ERROR_CODE + ":" + msg, comp.get_SourcePositionStart());
      }

    }

  }

}
