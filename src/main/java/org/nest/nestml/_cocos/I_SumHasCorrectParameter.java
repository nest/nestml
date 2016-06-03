/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.utils.ASTUtils;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.nest.symboltable.predefined.PredefinedFunctions.I_SUM;

/**
 * This class ensures that I_sum(I,Buffer) gets only simple expression
 *
 * @author plotnikov
 */
public class I_SumHasCorrectParameter implements ODEASTOdeDeclarationCoCo {
  public final static String ERROR_CODE = "NESTML_" + I_SumHasCorrectParameter.class.getSimpleName();

  @Override
  public void check(final ASTOdeDeclaration odeDeclaration) {
    final List<ASTFunctionCall> functions = ASTUtils.getAll(odeDeclaration, ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(I_SUM))
        .collect(toList());

    for (final ASTFunctionCall functionCall:functions) {
      for (final ASTExpr exprArgument:functionCall.getArgs()) {
        if (!exprArgument.variableIsPresent()) {
          error(exprArgument);
        }

      }

    }

  }

  /**
   * Creates an error message for the {@code exprArgument}.
   */
  private void error(final ASTExpr exprArgument) {
    CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();
    final String msg = errorStrings.getErrorMsg(this, ASTUtils.toString(exprArgument));

    Log.error(msg);
  }

}
