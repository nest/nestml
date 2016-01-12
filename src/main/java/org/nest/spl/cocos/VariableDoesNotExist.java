/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.cocos;

import com.google.common.collect.Lists;
import de.monticore.ast.ASTCNode;

import static de.se_rwth.commons.logging.Log.*;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.monticore.types.types._ast.ASTQualifiedName;
import de.monticore.utils.ASTNodes;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.*;
import org.nest.spl._cocos.*;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Checks that a referenced variable is also declared.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class VariableDoesNotExist implements
    SPLASTAssignmentCoCo,
    SPLASTFunctionCallCoCo,
    SPLASTDeclarationCoCo,
    SPLASTReturnStmtCoCo,
    SPLASTCompound_StmtCoCo {

  public static final String ERROR_CODE = "SPL_VARIABLE_DOES_NOT_EXIST";
  private static final String ERROR_MSG_FORMAT = "The variable %s is not defined in %s.";

  /**
   * Checks if the expression contains an undeclared variable.
   * @param expr Expression to check.
   */
  private void checkExpression(final ASTExpr expr) {
    checkState(expr.getEnclosingScope().isPresent());
    final Scope scope = expr.getEnclosingScope().get();
    final List<ASTQualifiedName> variables = ASTNodes.getSuccessors(expr, ASTQualifiedName.class);
    final List<ASTFunctionCall> functionCallAsts = ASTNodes.getSuccessors(expr, ASTFunctionCall.class);
    final List<String> functionNames = Lists.newArrayList();

    functionCallAsts.stream().forEach(functionCallAst ->
      functionNames.add(Names.getQualifiedName(functionCallAst.getQualifiedName().getParts()))
    );

    for (final ASTQualifiedName variable:variables) {
      final String variableName = Names.getQualifiedName(variable.getParts());
      if (isVariableName(functionNames, variableName)) {
        // todo refactor me
        final Optional<NESTMLVariableSymbol> variableSymbol
            = scope.resolve(variableName, NESTMLVariableSymbol.KIND);
        final Optional<NESTMLMethodSymbol> functionSymbol
            = scope.resolve(variableName, NESTMLMethodSymbol.KIND);
        if (!variableSymbol.isPresent() && !functionSymbol.isPresent()) {
          final String errorMsg = ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, variableName,
              scope.getName().orElse(""));
          error(errorMsg, variable.get_SourcePositionStart());
        }

      }

    }

  }

  private boolean isVariableName(List<String> functionNames, String variableName) {
    return !functionNames.contains(variableName);
  }

  @Override
  public void check(ASTCompound_Stmt node) {
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

  private void checkVariableByName(final String fqn, final ASTCNode node) {
    checkState(node.getEnclosingScope().isPresent());
    final Scope scope = node.getEnclosingScope().get();
    Optional<NESTMLVariableSymbol> variableSymbol = scope.resolve(fqn, NESTMLVariableSymbol.KIND);
    if (!variableSymbol.isPresent()) {
      error(ERROR_CODE + ":" +
          String.format(ERROR_MSG_FORMAT, fqn, scope.getName().orElse("")),
          node.get_SourcePositionStart());
    }

  }


  @Override
  public void check(final ASTAssignment astAssignment) {
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
    for (int i = 0; i< astFunctionCall.getArgList().getArgs().size(); ++i) {
      checkExpression(astFunctionCall.getArgList().getArgs().get(i));
    }

  }

  @Override
  public void check(final ASTReturnStmt astReturnStmt) {
    if (astReturnStmt.getExpr().isPresent()) {
      checkExpression(astReturnStmt.getExpr().get());
    }

  }

}
