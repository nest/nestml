/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTInputType;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Prohibits expression line a <- inhibitory inhibitory spike
 *
 * @author ippen, plotnikov
 */
public class MultipleInhExcModifiers implements NESTMLASTInputLineCoCo {

  public static final String ERROR_CODE = "NESTML_MULTIPLE_INH_EXC_MODIFIERS";
  NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();

  public void check(final ASTInputLine inputLine) {
    if (inputLine.isSpike()) {
      // get number of inh, exc keywords
      int inh = 0, exc = 0;
      for (ASTInputType inputType : inputLine.getInputTypes()) {
        if (inputType.isInhibitory()) {
          ++inh;
        } else if (inputType.isExcitatory()) {
          ++exc;
        }
      }

      if (inh > 1) {
        final String msg =  errorStrings.getErrorMsgMultipleInhibitory(this);
       error(msg, inputLine.get_SourcePositionStart());
      }

      if (exc > 1) {
        final String msg =  errorStrings.getErrorMsgMultipleExcitatory(this);
       error(msg, inputLine.get_SourcePositionStart());
      }

    }

  }

}
