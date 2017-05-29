/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTInputLine;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Current input lines cannot be inhibitory or excitatory:
 * buffer <- inhibitory current
 *
 * @author  ippen, plotnikov
 */
public class CurrentPortIsInhOrExc implements NESTMLASTInputLineCoCo {


  @Override
  public void check(ASTInputLine inputLine) {
    if (inputLine.isCurrent() ) {
      if (!inputLine.getInputTypes().isEmpty()) {
        NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsg(this);
       error(msg, inputLine.get_SourcePositionStart());
      }

    }

  }

}
