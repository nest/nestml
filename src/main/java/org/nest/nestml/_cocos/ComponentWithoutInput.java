/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTComponent;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Components are not allowed to have inputs, only neurons are.
 *
 * @author ippen, plotnikov
 */
public class ComponentWithoutInput implements NESTMLASTComponentCoCo {

  @Override
  public void check(final ASTComponent comp) {

    if (!comp.getBody().getInputLines().isEmpty()) {
      final String msg = NestmlErrorStrings.message(this, comp.getName(), comp.get_SourcePositionStart());

      error(msg, comp.get_SourcePositionStart());
    }

  }

}
