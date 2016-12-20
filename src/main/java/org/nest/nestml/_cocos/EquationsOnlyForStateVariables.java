/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._cocos.ODEASTEquationCoCo;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.utils.AstUtils.getNameOfLHS;

/**
 * Checks that equations are used only for variables from the the state block.
 *
 * @author plotnikov
 */
public class EquationsOnlyForStateVariables implements ODEASTEquationCoCo {
  public static final String ERROR_CODE = "NESTML_EQUATIONS_ONLY_FOR_STATE_VARIABLES";
  private final NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();

  @Override
  public void check(final ASTEquation astEq) {
    checkArgument(astEq.getEnclosingScope().isPresent(), "No scope was assigned. Please, run symboltable creator.");
    final Scope scope = astEq.getEnclosingScope().get();

    if (astEq.getLhs().getDifferentialOrder().size() > 0) {
      final Optional<VariableSymbol> variableSymbol = scope.resolve(astEq.getLhs().getSimpleName(), VariableSymbol.KIND);
      if (variableSymbol.isPresent()) {
        if (!variableSymbol.get().isState()) {
          final String msg = errorStrings.getErrorMsgAssignToNonState(this,variableSymbol.get().getName());

          Log.error(msg, astEq.get_SourcePositionStart());
        }
      }
      else {
        final String msg = errorStrings.getErrorMsgVariableNotDefined(this, astEq.getLhs().getSimpleName());
        Log.error(msg, astEq.get_SourcePositionStart());
      }

    }
    else {
      Log.warn(ERROR_CODE + ": The lefthandside of an equation must be a derivative, e.g. " + astEq.getLhs().toString() + "'");
    }

  }

}
