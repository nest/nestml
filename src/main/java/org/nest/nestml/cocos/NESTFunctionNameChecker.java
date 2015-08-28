package org.nest.nestml.cocos;


import com.google.common.collect.ImmutableSet;
import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;

import java.util.Set;

public class NESTFunctionNameChecker implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_F";

  private Set<String> nestFunNames = ImmutableSet.of(
      "update",
      "calibrate",
      "handle",
      "connect_sender",
      "check_connection",
      "get_status",
      "set_status",
      "init_state_",
      "init_buffers_");

  public void check(final ASTFunction fun) {
    if (fun != null && fun.getName() != null) {
      final String funName = fun.getName();

      if (nestFunNames.contains(funName)) {
        final String msg = "The function-name '" + funName
                + "' is already used by NEST. Please use another name.";
        error(ERROR_CODE + ":" + msg, fun.get_SourcePositionStart());
      }

    }

  }

}
