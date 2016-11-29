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
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getType;
import static org.nest.utils.AstUtils.computeTypeName;
import static org.nest.utils.AstUtils.getNameOfLHS;

import java.util.Optional;

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
    SPLASTELIF_ClauseCoCo  {

  @Override
  public void check(final ASTAssignment node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");

    //collect lhs information
    final String variableName = node.getLhsVarialbe().getName().toString();
    final Optional<VariableSymbol> lhsVariable = node.getEnclosingScope().get().resolve(
        variableName,
        VariableSymbol.KIND);
    final TypeSymbol variableType = lhsVariable.get().getType();

    //collect rhs information

    final Either<TypeSymbol,String> expressionType = node.getExpr().getType();
    if(expressionType.isValue()){

      if (!isCompatible(variableType,expressionType.getValue())) {
        final String msg = SplErrorStrings.messageAssignment(
            this,
            variableName,
            variableType.prettyPrint(),
            expressionType.getValue().prettyPrint(),
            node.get_SourcePositionStart());
        if (variableType.getType().equals(TypeSymbol.Type.UNIT)){ //assignee is unit -> drop warning not error
          warn(msg, node.get_SourcePositionStart());
        }
        else {
          error(msg, node.get_SourcePositionStart());
        }

      }
    }else {
      final String errorDescription = expressionType.getError();
      undefinedTypeError(node, errorDescription);
    }
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

      final Either<TypeSymbol, String> initializerExpressionType = node.getExpr().get().getType();
      final TypeSymbol variableDeclarationType;

      if (initializerExpressionType.isValue()) {
        variableDeclarationType = PredefinedTypes.getType(declarationTypeName);
        // TODO write a helper get assignable
        if (!isCompatible(variableDeclarationType, initializerExpressionType.getValue())) {
          final String msg = SplErrorStrings.messageInitType(
            this,
            varNameFromDeclaration,
            variableDeclarationType.prettyPrint(),
            initializerExpressionType.getValue().prettyPrint(),
            node.get_SourcePositionStart());
          if (variableDeclarationType.getType().equals(TypeSymbol.Type.UNIT)){ //assignee is unit -> drop warning not error
            warn(msg, node.get_SourcePositionStart());
          }
          else {
            error(msg, node.get_SourcePositionStart());
          }

        }

      }
      else {
        final String errorDescription = initializerExpressionType.getError();
        undefinedTypeError(node, errorDescription);
      }

    }

  }

  @Override
  public void check(final ASTELIF_Clause node) {
    final Either<TypeSymbol, String> exprType = node.getExpr().getType();

    if (exprType.isValue() && exprType.getValue() != getBooleanType()) {

      final String msg = SplErrorStrings.messageNonBoolean(
          this,
          exprType.getValue().prettyPrint(),
          node.get_SourcePositionStart());
      error(msg, node.get_SourcePositionStart());
    }

    if (exprType.isError()) {
      final String errorDescription = exprType.getError() ;
      undefinedTypeError(node, errorDescription);
    }

  }

  @Override
  public void check(final ASTFOR_Stmt node) {
    // TODO
  }

  @Override
  public void check(final ASTIF_Clause node) {
    final Either<TypeSymbol, String> exprType = node.getExpr().getType();

    if (exprType.isValue() && exprType.getValue() != getBooleanType()) {
      final String msg = SplErrorStrings.messageNonBoolean(
          this,
          exprType.getValue().prettyPrint(),
          node.get_SourcePositionStart());
      error(msg, node.get_SourcePositionStart());

    }

    if (exprType.isError()) {
      final String errorDescription = exprType.getError();
      undefinedTypeError(node, errorDescription);
    }

  }

  @Override
  public void check(final ASTWHILE_Stmt node) {
    if (node.getExpr().getType().getValue() != getBooleanType()) {
      final String msg = SplErrorStrings.messageNonBoolean(
          this,
          node.getExpr().getType().getValue().prettyPrint(),
          node.get_SourcePositionStart());
      error(msg, node.get_SourcePositionStart());

    }

  }

  private void undefinedTypeError(final ASTNode node, final String reason) {
    final String msg = SplErrorStrings.messageInvalidExpression(this, reason, node.get_SourcePositionStart());
    error(msg, node.get_SourcePositionStart());
  }

}
