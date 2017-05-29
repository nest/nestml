/*
 * VariableDoesNotExist.java
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

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._cocos.NestmlErrorStrings;
import org.nest.ode._ast.ASTDerivative;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that all variables, which are used in an ODE declaration are defined
 *
 * @author  plotnikov
 */
public class VariableDoesNotExist implements ODEASTOdeDeclarationCoCo {

  @Override
  public void check(final ASTOdeDeclaration node) {
    node.getOdeFunctions().forEach(
        oderAlias-> {
          checkVariableByName(oderAlias.getVariableName(), node);
          AstUtils
              .getAll(oderAlias.getExpr(), ASTVariable.class)
              .forEach(variable -> checkVariableByName(variable.toString(), variable));
        }
    );
    node.getShapes().forEach(
        ode-> AstUtils
            .getAll(ode.getRhs(), ASTVariable.class)
            .forEach(variable -> checkVariableByName(variable.toString(), variable))
    );
    node.getEquations().forEach(
        ode-> {
          checkVariableByName(ode.getLhs());
          AstUtils.getAll(ode.getRhs(), ASTVariable.class)
                  .forEach(variable -> checkVariableByName(variable.toString(), variable)); // it can be a D'' variable
        }

    );

  }

  private void checkVariableByName(final ASTDerivative astDerivative) {
    if (astDerivative.getDifferentialOrder().size() == 0) {
      checkVariableByName(astDerivative.toString(), astDerivative);
    }
    else {
      checkVariableByName(AstUtils.getNameOfLHS(astDerivative), astDerivative);
    }

  }

  private void checkVariableByName(final String variableName, final ASTNode node) {
    checkState(node.getEnclosingScope().isPresent());
    final Scope scope = node.getEnclosingScope().get();

    if (!exists(variableName, scope)) {
      error(NestmlErrorStrings.getErrorMsg(this, variableName), node.get_SourcePositionStart());
    }

  }

  private boolean exists(final String variableName, final Scope scope) {
    return scope.resolveMany(variableName, VariableSymbol.KIND).size() > 0;
  }

}
