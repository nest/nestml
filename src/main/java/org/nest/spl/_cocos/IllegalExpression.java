/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.monticore.ast.ASTNode;
import org.nest.spl._ast.*;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTUtils;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.utils.ASTUtils.computeTypeName;

/**
 * Check that the type of the loop variable is an integer.
 *
 * @author ippen, plotnikov
 */
public class IllegalExpression implements
    SPLASTIF_ClauseCoCo,
    SPLASTFOR_StmtCoCo,
    SPLASTWHILE_StmtCoCo,
    SPLASTAssignmentCoCo,
    SPLASTDeclarationCoCo,
    SPLASTELIF_ClauseCoCo

{
  public static final String ERROR_CODE = "SPL_ILLEGAL_EXPRESSION";

  @Override
  public void check(final ASTAssignment node) {
    // TODO
  }

  @Override
  public void check(final ASTDeclaration node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");

    // compute the symbol of the var from the declaration.
    // take an arbitrary var since the variables in the declaration
    // share the same type
    if (node.getExpr().isPresent()) {
      final String varNameFromDeclaration = node.getVars().get(0);
      final String declarationTypeName = computeTypeName(node.getDatatype());

      final Either<TypeSymbol, String> initializerExpressionType = node.getExpr().get().computeType().get();
      final TypeSymbol variableDeclarationType;

      if (initializerExpressionType.isValue()) {
        variableDeclarationType = PredefinedTypes.getType(declarationTypeName);
        // TODO write a helper get assignable
        if (!isCompatible(variableDeclarationType, initializerExpressionType.getValue())) {
          if (variableDeclarationType.getType().equals(TypeSymbol.Type.UNIT) &&
              initializerExpressionType.getValue().getType().equals(TypeSymbol.Type.UNIT)) {
            final String msg = "Cannot initialize variable " +varNameFromDeclaration+" of type "
                + variableDeclarationType.prettyPrint()+" with an expression of type: " +
                initializerExpressionType.getValue().prettyPrint() +
                node.get_SourcePositionStart();
            warn(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
          }
          else {
            final String msg = "Cannot initialize variable " +varNameFromDeclaration+" of type "
                + variableDeclarationType.prettyPrint() +" with an expression of type: " +
                initializerExpressionType.getValue().prettyPrint() +
                node.get_SourcePositionStart();
            error(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
          }

        }

      }
      else {
        final String errorDescription = initializerExpressionType.getError() +
            "Problem with the expression: " + ASTUtils.toString(node.getExpr().get());
        undefinedTypeError(node, errorDescription);
      }

    }

  }

  @Override
  public void check(final ASTELIF_Clause node) {
    final Either<TypeSymbol, String> exprType = node.getExpr().computeType().get();

    if (exprType.isValue() && exprType.getValue() != getBooleanType()) {
      final String msg = "Cannot use non boolean expression of type " + exprType.getValue();
      error(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
    }

    if (exprType.isError()) {
      final String errorDescription = exprType.getError() +
          "Problem with the expression: " + ASTUtils.toString(node.getExpr());
      undefinedTypeError(node, errorDescription);
    }

  }

  @Override
  public void check(final ASTFOR_Stmt node) {
    // TODO
  }

  @Override
  public void check(final ASTIF_Clause node) {
    final Either<TypeSymbol, String> exprType = node.getExpr().computeType().get();

    if (exprType.isValue() && exprType.getValue() != getBooleanType()) {
      final String msg = "Cannot use non boolean expression of type " + exprType.getValue();
      error(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
    }

    if (exprType.isError()) {
      final String errorDescription = exprType.getError() +
          "Problem with the expression: " + ASTUtils.toString(node.getExpr());
      undefinedTypeError(node, errorDescription);
    }

  }

  @Override
  public void check(final ASTWHILE_Stmt node) {
    try {
      if (node.getExpr().computeType().get().getValue() != getBooleanType()) {
        final String msg = "Cannot use non boolean expression in a while statement " +
            "@" + node.get_SourcePositionStart();
       error(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
      }
    }
    catch (RuntimeException e) {
      final String msg = "Cannot initialize variable with an expression of type: " +
          "@" + node.get_SourcePositionStart();
     error(ERROR_CODE + ":" +  msg, node.get_SourcePositionStart());
    }


  }

  private void undefinedTypeError(final ASTNode node, final String reason) {
    error(ERROR_CODE + ":" +  reason, node.get_SourcePositionStart());
  }

}
