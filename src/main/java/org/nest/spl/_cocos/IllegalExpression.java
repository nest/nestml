/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl._ast.*;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.spl._cocos.SplErrorStrings.messageCastToReal;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isReal;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.utils.AstUtils.computeTypeName;

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
    if(node.isAssignment()){
      handleAssignment(node);
    }
    //compound assignments: Construct dummy '=' assignment node with a conventional expression and test it instead
    else{

      ASTExpr dummyVariableExpr = ASTExpr.getBuilder().variable(node.getLhsVarialbe()).build();
      dummyVariableExpr.setEnclosingScope(node.getEnclosingScope().get());
      //TODO: Correctly calculate source positions
      dummyVariableExpr.set_SourcePositionStart(node.get_SourcePositionStart());

      ASTExpr.Builder exprBuilder = ASTExpr.getBuilder();
      if(node.isCompoundProduct()){
        exprBuilder.timesOp(true);
      }
      if(node.isCompoundSum()){
        exprBuilder.plusOp(true);
      }
      if(node.isCompoundQuotient()){
        exprBuilder.divOp(true);
      }
      if(node.isCompoundMinus()){
        exprBuilder.minusOp(true);
      }
      ASTExpr dummyExpression = exprBuilder.left(dummyVariableExpr).right(node.getExpr()).build();
      dummyExpression.setEnclosingScope(node.getEnclosingScope().get());
      //TODO: Correctly calculate source positions
      dummyExpression.set_SourcePositionStart(node.get_SourcePositionStart());

      ASTAssignment dummyAssignment = ASTAssignment.getBuilder()
          .assignment(true)
          .lhsVarialbe(node.getLhsVarialbe())
          .expr(dummyExpression)
          .build();

      dummyAssignment.setEnclosingScope(node.getEnclosingScope().get());
      //TODO: Correctly calculate source positions
      dummyAssignment.set_SourcePositionStart(node.get_SourcePositionStart());

      handleAssignment(dummyAssignment);

    }



  }

  private void handleAssignment(
      ASTAssignment node){
    //collect lhs information
    final String variableName = node.getLhsVarialbe().getName().toString();
    final Optional<VariableSymbol> lhsVariable = node.getEnclosingScope().get().resolve(
        variableName,
        VariableSymbol.KIND);
    final TypeSymbol variableType = lhsVariable.get().getType();

    //collect rhs information

    final Either<TypeSymbol,String> expressionTypeEither = node.getExpr().getType();
    if(expressionTypeEither.isValue()){
      final TypeSymbol expressionType = expressionTypeEither.getValue();
      if (!isCompatible(variableType,expressionType)) {
        final String msg = SplErrorStrings.messageAssignment(
            this,
            variableName,
            variableType.prettyPrint(),
            expressionType.prettyPrint(),
            node.get_SourcePositionStart());
        if(isReal(variableType)&&isUnit(expressionType)){
          //TODO put in string class when I inevitably refactor it.
          final String castMsg = messageCastToReal(this, expressionType.prettyPrint(), node.getExpr().get_SourcePositionStart());
          warn(castMsg);
        } else if (isUnit(variableType)){ //assignee is unit -> drop warning not error
          warn(msg, node.get_SourcePositionStart());
        }
        else {
          error(msg, node.get_SourcePositionStart());
        }
      }
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
          if(isReal(variableDeclarationType)&&isUnit(initializerExpressionType.getValue())){
            //TODO put in string class when I inevitably refactor it.


            final String castMsg = messageCastToReal(
                this,
                initializerExpressionType.getValue().prettyPrint(),
                node.getExpr().get().get_SourcePositionStart());
            warn(castMsg);
          }else if (isUnit(variableDeclarationType)){ //assignee is unit -> drop warning not error
            warn(msg, node.get_SourcePositionStart());
          }
          else {
            error(msg, node.get_SourcePositionStart());
          }

        }

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

}
