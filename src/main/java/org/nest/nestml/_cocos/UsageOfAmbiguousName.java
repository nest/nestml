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
package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.symboltable.Symbol;
import de.monticore.utils.ASTNodes;
import org.nest.nestml._ast.*;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Collection;
import java.util.List;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that all variables, which are used in an ODE declaration are defined
 *
 * @author  plotnikov
 */
public class UsageOfAmbiguousName implements
    NESTMLASTOdeDeclarationCoCo,
    NESTMLASTAssignmentCoCo,
    NESTMLASTFunctionCallCoCo,
    NESTMLASTDeclarationCoCo,
    NESTMLASTReturnStmtCoCo,
    NESTMLASTCompound_StmtCoCo{

  @Override
  public void check(final ASTCompound_Stmt node) {
    if (node.getIF_Stmt().isPresent()) {
      checkExpression(node.getIF_Stmt().get().getIF_Clause().getExpr());
      node.getIF_Stmt().get().getELIF_Clauses().forEach(elifAst -> checkExpression(elifAst.getExpr()));
    }

    else if (node.getFOR_Stmt().isPresent()) {
      checkVariableByName(node.getFOR_Stmt().get().getVar(), node);
      checkExpression(node.getFOR_Stmt().get().getFrom());
      checkExpression(node.getFOR_Stmt().get().getTo());
    }
    else if (node.getWHILE_Stmt().isPresent()) {
      checkExpression(node.getWHILE_Stmt().get().getExpr());
    }
    else {
      // cannot happen. the grammar doesn't contain other alternatives.
      checkState(false);
    }

  }

  @Override
  public void check(final ASTAssignment astAssignment) {
    checkVariableByName(astAssignment.getLhsVarialbe().toString(), astAssignment);

    checkExpression(astAssignment.getExpr());
  }

  @Override
  public void check(final ASTDeclaration astDeclaration) {
    if (astDeclaration.getExpr().isPresent()) {
      checkExpression(astDeclaration.getExpr().get());
    }

  }

  @Override
  public void check(final ASTFunctionCall astFunctionCall) {
    for (int i = 0; i < astFunctionCall.getArgs().size(); ++i) {
      checkExpression(astFunctionCall.getArgs().get(i));
    }

  }

  @Override
  public void check(final ASTReturnStmt astReturnStmt) {
    if (astReturnStmt.getExpr().isPresent()) {
      checkExpression(astReturnStmt.getExpr().get());
    }

  }

  /**
   * Checks if the expression contains an undefined variables.
   */
  private void checkExpression(final ASTExpr expr) {
    checkState(expr.getEnclosingScope().isPresent());
    final Scope scope = expr.getEnclosingScope().get();
    final List<ASTVariable> variables = ASTNodes.getSuccessors(expr, ASTVariable.class);

    for (final ASTVariable variable : variables) {
      final String variableName = variable.toString();

      checkVariableByName(variableName, variable);

    }

  }


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
        shape-> AstUtils
            .getAll(shape.getRhs(), ASTVariable.class)
            .forEach(variable -> checkVariableByName(variable.toString(), variable))
    );

    node.getEquations().forEach(
        ode-> {
          checkVariableByName(ode.getLhs().getNameOfDerivedVariable(), ode);
          AstUtils.getAll(ode.getRhs(), ASTVariable.class)
                  .forEach(variable -> checkVariableByName(variable.toString(), variable)); // it can be a D'' variable
        }

    );

  }

  private void checkVariableByName(final String variableName, final ASTNode node) {
    checkState(node.getEnclosingScope().isPresent());
    final Scope scope = node.getEnclosingScope().get();
    int symboDefinitions = scope.resolveMany(variableName, VariableSymbol.KIND).size();
    if (symboDefinitions == 0) {
      error(NestmlErrorStrings.messageVariableNotDefined(this, variableName), node.get_SourcePositionStart());

    }
    else if (symboDefinitions > 1) {
      error(NestmlErrorStrings.messageVariableDefinedMultipleTimes(this, variableName), node.get_SourcePositionStart());
    }

  }

}
