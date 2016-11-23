/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTComponent;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Components are not allowed to have output, only neurons are.
 *
 * @author  ippen, plotnikov
 */
public class ComponentWithoutOutput implements NESTMLASTComponentCoCo {

  @Override
  public void check(ASTComponent comp) {
    if (!comp.getBody().getOutputs().isEmpty()) {
      final String msg = NestmlErrorStrings.message(this, comp.getName(), comp.get_SourcePositionStart());

     error(msg, comp.get_SourcePositionStart());
    }

  }

}
