package org.nest.nestml.cocos;


import de.monticore.cocos.CoCoLog;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTInputType;
import org.nest.nestml._cocos.NESTMLASTInputLineCoCo;

public class MultipleInhExcInput implements NESTMLASTInputLineCoCo {

  public static final String ERROR_CODE = "NESTML_MULTIPLE_INH_EXC_INPUT";

  public void check(ASTInputLine inputLine) {
    if (inputLine != null && inputLine.isSpike()
            && inputLine.getInputTypes() != null) {
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
        CoCoLog.error(ERROR_CODE, msg, inputLine.get_SourcePositionStart());
      }

      if (exc > 1) {
        final String msg =  "Multiple occurrences of the keyword 'excitatory' are not allowed.";
        CoCoLog.error(ERROR_CODE, msg, inputLine.get_SourcePositionStart());
      }

    }

  }

}
