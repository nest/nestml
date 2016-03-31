/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.cocos;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTCNode;
import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.*;
import org.nest.spl._cocos.*;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static java.util.stream.Collectors.toList;

/**
 * Checks that a referenced variable is also declared.
 *
 * @author plotnikov
 */
public class VariableDoesNotExist implements
    SPLASTAssignmentCoCo,
    SPLASTFunctionCallCoCo,
    SPLASTDeclarationCoCo,
    SPLASTReturnStmtCoCo,
    SPLASTCompound_StmtCoCo,
    SPLASTOdeDeclarationCoCo {

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

  private void checkVariableByName(final String fqn, final ASTNode node) {
    checkState(node.getEnclosingScope().isPresent());
    final Scope scope = node.getEnclosingScope().get();

    if (!exists(fqn, scope)) {
      error(ERROR_CODE + ":" +
              String.format(ERROR_MSG_FORMAT, fqn, scope.getName().orElse("")),
          node.get_SourcePositionStart());
    }

  }

  @Override
  public void check(final ASTAssignment astAssignment) {
    final String lhsVariables = Names.getQualifiedName(astAssignment.getVariableName().getParts());
    checkVariableByName(lhsVariables, astAssignment);
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
    for (int i = 0; i < astFunctionCall.getArgList().getArgs().size(); ++i) {
      checkExpression(astFunctionCall.getArgList().getArgs().get(i));
    }

  }

  @Override
  public void check(final ASTReturnStmt astReturnStmt) {
    if (astReturnStmt.getExpr().isPresent()) {
      checkExpression(astReturnStmt.getExpr().get());
    }

  }

  protected List<ASTQualifiedName> getVariablesFromExpressions(final ASTExpr expression) {
    final List<ASTQualifiedName> names = ASTNodes
        .getSuccessors(expression, ASTQualifiedName.class);

    final List<String> functions = ASTNodes
        .getSuccessors(expression, ASTFunctionCall.class).stream()
        .map(ASTFunctionCall::getCalleeName)
        .collect(Collectors.toList());

    return names.stream()
        .filter(name -> !functions.contains(Names.getQualifiedName(name.getParts())))
        .collect(toList());
  }

  @Override
  public void check(ASTOdeDeclaration node) {
    node.getODEs().forEach(
        ode-> {
          checkVariableByName(ode.getLhsVariable(), node);
          getVariablesFromExpressions(ode.getRhs()).forEach(
              variable -> checkVariableByName(Names.getQualifiedName(variable.getParts()), node));
        }

    );

    node.getEqs().forEach(
        eq-> {
          checkVariableByName(eq.getLhsVariable(), node);
          getVariablesFromExpressions(eq.getRhs()).forEach(
              variable -> checkVariableByName(Names.getQualifiedName(variable.getParts()), node));
        }

    );
  }
}
