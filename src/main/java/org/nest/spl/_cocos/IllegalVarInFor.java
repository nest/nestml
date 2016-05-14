/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTFOR_Stmt;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Check that the type of the loop variable is an integer.
 * TODO this coco fails, if variable is not defined
 * @author plotnikov
 */
public class IllegalVarInFor implements SPLASTFOR_StmtCoCo {
  public static final String ERROR_CODE = "SPL_ILLEGAL_VAR_IN_FOR";

  private static final String ERROR_MSG_FORMAT = "The type of the iterator in a for-loop must be numeric and not: '%s' .";

  @Override
  public void check(final ASTFOR_Stmt astfor) {
    checkArgument(astfor.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = astfor.getEnclosingScope().get();

    String iterName = astfor.getVar();

    final VariableSymbol iter = VariableSymbol.resolve(iterName, scope);
    TypeChecker tc = new TypeChecker();
    if (!tc.checkNumber(iter.getType())) {
      Log.error(ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, iter.getType()), astfor.get_SourcePositionEnd());
    }

  }

}
