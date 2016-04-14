/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.ode._ast.ASTEq;
import org.nest.ode._ast.ASTODE;
import org.nest.ode._cocos.ODEASTEqCoCo;
import org.nest.ode._cocos.ODEASTODECoCo;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Checks that equations are used only to define state variables
 *
 * @author plotnikov
 */
public class EquationsOnlyForStateVariables implements ODEASTEqCoCo, ODEASTODECoCo {
  public static final String ERROR_CODE = "NESTML_EQUATIONS_ONLY_FOR_STATE_VARIABLES";
  CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();

  @Override
  public void check(final ASTEq astEq) {
    checkArgument(astEq.getEnclosingScope().isPresent(), "No scope was assigned. Please, run symboltable creator.");
    final Scope scope = astEq.getEnclosingScope().get();
    final Optional<VariableSymbol> variableSymbol
        = NESTMLSymbols.resolve(astEq.getLhs().toString(), scope);
    checkVariable(variableSymbol, astEq);
  }

  @Override
  public void check(final ASTODE astOde) {
    checkArgument(astOde.getEnclosingScope().isPresent(), "No scope was assigned. Please, run symboltable creator.");
    final Scope scope = astOde.getEnclosingScope().get();
    final Optional<VariableSymbol> variableSymbol
        = NESTMLSymbols.resolve(astOde.getLhs().toString(), scope);
    checkVariable(variableSymbol, astOde);
  }

  private void checkVariable(final Optional<VariableSymbol> variableSymbol, final ASTNode node) {
    if (variableSymbol.isPresent()) {
      if (!variableSymbol.get().isInState()) {
        final String msg = errorStrings.getErrorMsgAssignToNonState(this,variableSymbol.get().getName());

        Log.error(msg, node.get_SourcePositionStart());
      }
    }
    else {
      final String msg = errorStrings.getErrorMsgVariableNotDefined(this);
      Log.warn(msg, node.get_SourcePositionStart());
    }

  }
}
