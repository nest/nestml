/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import com.google.common.collect.ImmutableSet;
import org.nest.nestml._ast.ASTFunction;

import java.util.Set;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks collisions with generated functions.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
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
        CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
        final String msg = errorStrings.getErrorMsg(this,funName);

        error(msg, fun.get_SourcePositionStart());
      }

    }

  }

}
