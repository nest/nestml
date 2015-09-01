/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import static de.se_rwth.commons.logging.Log.error;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTInputType;
import org.nest.nestml._cocos.NESTMLASTInputLineCoCo;

/**
 * Prohibits expression line a <- inhibitory inhibitory spike
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class MultipleInhExcInput implements NESTMLASTInputLineCoCo {

  public static final String ERROR_CODE = "NESTML_MULTIPLE_INH_EXC_INPUT";

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
        final String msg =  "Multiple occurrences of the keyword 'inhibitory' are not allowed.";
       error(ERROR_CODE + ":" +  msg, inputLine.get_SourcePositionStart());
      }

      if (exc > 1) {
        final String msg =  "Multiple occurrences of the keyword 'excitatory' are not allowed.";
       error(ERROR_CODE + ":" +  msg, inputLine.get_SourcePositionStart());
      }

    }

  }

}
