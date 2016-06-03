/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.ode._ast.ASTOdeDeclaration;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.spl._ast.ASTAssignment;
import org.nest.spl._ast.ASTCompound_Stmt;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTReturnStmt;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTUtils;

import java.util.List;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Checks that a referenced variable is also declared.
 *
 * @author plotnikov
 */
public class VariableDoesNotExist implements
    SPLASTAssignmentCoCo,
    CommonsASTFunctionCallCoCo,
    SPLASTDeclarationCoCo,
    SPLASTReturnStmtCoCo,
    SPLASTCompound_StmtCoCo,
    ODEASTOdeDeclarationCoCo {

  public static final String ERROR_CODE = "SPL_VARIABLE_DOES_NOT_EXIST";

  private static final String ERROR_MSG_FORMAT = "The variable %s is not defined in %s.";

  /**
   * Checks if the expression contains an undefined variables.
   * TODO refactor me
   */
  private void checkExpression(final ASTExpr expr) {
    checkState(expr.getEnclosingScope().isPresent());
    final Scope scope = expr.getEnclosingScope().get();
    final List<ASTQualifiedName> variables = ASTNodes.getSuccessors(expr, ASTQualifiedName.class);
    final List<ASTFunctionCall> functionCallAsts = ASTNodes
        .getSuccessors(expr, ASTFunctionCall.class);
    final List<String> functionNames = Lists.newArrayList();

    functionCallAsts.stream().forEach(astFunctionCall ->
        functionNames.add(astFunctionCall.getCalleeName())
    );

    for (final ASTQualifiedName variable : variables) {
      final String variableName = Names.getQualifiedName(variable.getParts());
      if (isVariableName(functionNames, variableName)) {

        if (!exists(variableName, scope)) {
          final String errorMsg = ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, variableName,
              scope.getName().orElse(""));
          error(errorMsg, variable.get_SourcePositionStart());
        }

      }

    }

  }

  private boolean exists(final String variableName, final Scope scope) {
    return scope.resolve(variableName, VariableSymbol.KIND).isPresent();
  }

  private boolean isVariableName(
      final List<String> functionNames,
      final String variableName) {
    return !functionNames.contains(variableName);
  }

  @Override
  public void check(final ASTCompound_Stmt node) {
    if (node.getIF_Stmt().isPresent()) {
      checkExpression(node.getIF_Stmt().get().getIF_Clause().getExpr());
    }
    else if (node.getFOR_Stmt().isPresent()) {
      checkVariableByName(node.getFOR_Stmt().get().getVar(), node);
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
    checkVariableByName(astAssignment.getLhsVarialbe(), astAssignment);
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

  @Override
  public void check(final ASTOdeDeclaration node) {
    node.getEquations().forEach(
        ode-> {
          checkVariableByName(ode.getLhs().getName().toString(), node);
          ASTUtils.getAll(ode.getRhs(), ASTVariable.class).forEach(
              variable -> checkVariableByName(Names.getQualifiedName(variable.getName().getParts()), node));
        }

    );

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
}
