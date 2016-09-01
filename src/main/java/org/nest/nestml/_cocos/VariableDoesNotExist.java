/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import org.nest.commons._ast.ASTVariable;
import org.nest.ode._ast.ASTDerivative;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that all variables, which are used in an ODE declaration are defined
 *
 * @author  plotnikov
 */
public class VariableDoesNotExist implements ODEASTOdeDeclarationCoCo {

  public static final String ERROR_CODE = "NESTML_VARIABLE_DOESNT_EXIST";
  private static final String ERROR_MSG_FORMAT = "The variable %s is not defined in %s.";



  @Override
  public void check(final ASTOdeDeclaration node) {
    node.getODEAliass().forEach(
        oderAlias-> {
          checkVariableByName(oderAlias.getVariableName(), node);
          ASTUtils
              .getAll(oderAlias.getExpr(), ASTVariable.class)
              .forEach(variable -> checkVariableByName(variable.toString(), node));
        }
    );
    node.getShapes().forEach(
        ode-> ASTUtils
            .getAll(ode.getRhs(), ASTVariable.class)
            .forEach(variable -> checkVariableByName(variable.toString(), node))
    );
    node.getEquations().forEach(
        ode-> {
          checkVariableByName(ode.getLhs());
          ASTUtils.getAll(ode.getRhs(), ASTVariable.class)
                  .forEach(variable -> checkVariableByName(variable.getName().toString(), node)); // it can be a D'' variable
        }

    );

  }

  private void checkVariableByName(final ASTDerivative astDerivative) {
    if (astDerivative.getDifferentialOrder().size() == 0) {
      checkVariableByName(astDerivative.toString(), astDerivative);
    }
    else {
      checkVariableByName(ASTUtils.getNameOfLHS(astDerivative), astDerivative);
    }

  }

  private void checkVariableByName(final String variableName, final ASTNode node) {
    checkState(node.getEnclosingScope().isPresent());
    final Scope scope = node.getEnclosingScope().get();

    if (!exists(variableName, scope)) {
      error(ERROR_CODE + ":" +
            String.format(ERROR_MSG_FORMAT, variableName, scope.getName().orElse("")),
          node.get_SourcePositionStart());
    }

  }

  private boolean exists(final String variableName, final Scope scope) {
    return scope.resolve(variableName, VariableSymbol.KIND).isPresent();
  }

}
