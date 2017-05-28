/*
 * EquationsOnlyForStateVariables.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.ode._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.ode._ast.ASTEquation;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

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
