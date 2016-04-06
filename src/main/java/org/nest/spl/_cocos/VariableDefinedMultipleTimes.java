/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import com.google.common.collect.Maps;
import static de.se_rwth.commons.logging.Log.error;
import de.se_rwth.commons.SourcePosition;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTBlock;
import org.nest.spl._ast.ASTSmall_Stmt;
import org.nest.spl._ast.ASTStmt;

import java.util.Map;

/**
 * Checks that a referenced variable is also declared.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class VariableDefinedMultipleTimes implements SPLASTBlockCoCo {
  public static final String ERROR_CODE = "SPL_VARIABLE_EXISTS_MULTIPLE_TIMES";
  private static final String ERROR_MSG_FORMAT = "The variable %s defined multiple times.";

  private final Map<String, SourcePosition> names = Maps.newHashMap();

  @Override
  public void check(ASTBlock block) {
    if (block != null && block.getStmts() != null) {
      resetNames();
      additionalNames(block);
      doCheck(block);
    }
  }

  public void additionalNames(ASTBlock block) {
  }

  /**
   * TODO refactor it as the inspection suppose
   *
   * @param block
   */
  protected void doCheck(ASTBlock block) {
    for (ASTStmt stmt : block.getStmts()) {
      if (stmt.getSimple_Stmt().isPresent() && stmt.getSimple_Stmt().get().getSmall_Stmts() != null) {
        for (ASTSmall_Stmt small : stmt.getSimple_Stmt().get().getSmall_Stmts()) {
          if (small.getDeclaration().isPresent()) {
            for (String var : small.getDeclaration().get().getVars()) {
              addVariable(var, small.getDeclaration().get().get_SourcePositionStart(), getNames());
            }
          }
        }
      }
    }
  }

  protected Map<String, SourcePosition> getNames() {
    return names;
  }

  protected void resetNames() {
    names.clear();
  }

  protected void addVariable(String name, SourcePosition sourcePosition, Map<String, SourcePosition> names) {
    if (names.containsKey(name)) {
      Log.error(ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, name), sourcePosition);

    } else {
      names.put(name, sourcePosition);
    }
  }

}
