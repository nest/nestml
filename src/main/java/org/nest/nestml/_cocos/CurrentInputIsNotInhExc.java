/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTInputLine;

/**
 * Current input lines cannot be inhibitory aor excitatory:
 * currentBuffer <- current
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class CurrentInputIsNotInhExc implements NESTMLASTInputLineCoCo {

  public static final String ERROR_CODE = "NESTML_CURRENT_INPUT_IS_NOT_INH_EXC";

  @Override
  public void check(ASTInputLine inputLine) {
    if (inputLine.isCurrent() ) {
      if (!inputLine.getInputTypes().isEmpty()) {
        final String msg = "Current input can neither be inhibitory nor excitatory.";
       error(ERROR_CODE + ":" +  msg, inputLine.get_SourcePositionStart());
      }

    }

  }

}
