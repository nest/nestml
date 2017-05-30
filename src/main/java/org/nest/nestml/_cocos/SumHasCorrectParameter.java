/*
 * SumHasCorrectParameter.java
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
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.nestml._ast.ASTOdeDeclaration;
import org.nest.utils.AstUtils;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.nest.symboltable.predefined.PredefinedFunctions.COND_SUM;
import static org.nest.symboltable.predefined.PredefinedFunctions.CURR_SUM;

/**
 * This class ensures that curr_sum(I,Buffer) gets only simple expression
 *
 * @author plotnikov
 */
public class SumHasCorrectParameter implements NESTMLASTOdeDeclarationCoCo {

  @Override
  public void check(final ASTOdeDeclaration odeDeclaration) {
    final List<ASTFunctionCall> functions = AstUtils.getAll(odeDeclaration, ASTFunctionCall.class)
        .stream()
        .filter(astFunctionCall -> astFunctionCall.getCalleeName().equals(CURR_SUM) ||
                                   astFunctionCall.getCalleeName().equals(COND_SUM))
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
    final String msg = NestmlErrorStrings.message(this, AstUtils.toString(exprArgument));

    Log.error(msg);
  }

}
