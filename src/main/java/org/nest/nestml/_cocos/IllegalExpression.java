/*
 * IllegalExpression.java
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

import com.google.common.base.Strings;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._visitor.ExpressionTypeVisitor;
import org.nest.nestml._ast.*;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.typechecking.TypeChecker;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.*;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.utils.AstUtils.computeTypeName;

/**
 * Check that the type of the loop variable is an integer.
 *
 * @author ippen, plotnikov
 */
public class IllegalExpression implements
    NESTMLASTIF_ClauseCoCo,
    NESTMLASTFOR_StmtCoCo,
    NESTMLASTWHILE_StmtCoCo,
    NESTMLASTAssignmentCoCo,
    NESTMLASTDeclarationCoCo,
    NESTMLASTELIF_ClauseCoCo  {

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
    final String variableName = node.getLhsVarialbe().getName() + Strings.repeat("'", node.getLhsVarialbe().getDifferentialOrder().size());
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
            expressionType.prettyPrint());
        if(isReal(variableType)&&isUnit(expressionType)){
          //TODO put in string class when I inevitably refactor it.
          final String castMsg = SplErrorStrings.messageCastToReal(this, expressionType.prettyPrint());
          warn(castMsg, node.get_SourcePositionStart());
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
      final String varNameFromDeclaration = node.getVars().get(0).toString();
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
            initializerExpressionType.getValue().prettyPrint());
          if(isReal(variableDeclarationType)&&isUnit(initializerExpressionType.getValue())){
            //TODO put in string class when I inevitably refactor it.


            final String castMsg = SplErrorStrings.messageCastToReal(
                this,
                initializerExpressionType.getValue().prettyPrint());
            warn(castMsg, node.get_SourcePositionStart());
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
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Either<TypeSymbol, String> exprType = node.getExpr().getType();

    if (exprType.isValue() && !exprType.getValue().equals(getBooleanType())) {

      final String msg = SplErrorStrings.messageNonBoolean(this, exprType.getValue().prettyPrint());
      error(msg, node.get_SourcePositionStart());
    }

  }

  @Override
  public void check(final ASTFOR_Stmt astfor) {
    checkArgument(astfor.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Scope scope = astfor.getEnclosingScope().get();

    String iterName = astfor.getVar();

    final VariableSymbol iter = VariableSymbol.resolve(iterName, scope);
    TypeChecker tc = new TypeChecker();
    if (!tc.checkNumber(iter.getType())) {
      final String msg = SplErrorStrings.messageForLoop(this, iterName, iter.getType().getName());
      Log.error(msg);
    }

    final ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
    astfor.getFrom().accept(expressionTypeVisitor);

    if (astfor.getFrom().getType().isValue()) {
      if (!tc.checkNumber(astfor.getFrom().getType().getValue())) {
        final String msg = SplErrorStrings.messageForLoopBound(
            this,
            AstUtils.toString(astfor.getFrom()),
            astfor.getFrom().getType().getValue().getName());
        Log.error(msg);
      }
    }

    astfor.getTo().accept(expressionTypeVisitor);
    astfor.getTo().accept(expressionTypeVisitor);
    if (astfor.getTo().getType().isValue()) {
      if (!tc.checkNumber(astfor.getTo().getType().getValue())) {
        final String msg = SplErrorStrings.messageForLoopBound(
            this,
            AstUtils.toString(astfor.getTo()),
            astfor.getTo().getType().getValue().getName());
        Log.error(msg);
      }
    }
  }

  @Override
  public void check(final ASTIF_Clause node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    final Either<TypeSymbol, String> exprType = node.getExpr().getType();

    if (exprType.isValue() && !exprType.getValue().equals(getBooleanType())) {
      final String msg = SplErrorStrings.messageNonBoolean(this, exprType.getValue().prettyPrint());
      error(msg, node.get_SourcePositionStart());

    }

  }

  @Override
  public void check(final ASTWHILE_Stmt node) {
    checkArgument(node.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");
    if (!node.getExpr().getType().getValue().equals(getBooleanType())) {
      final String msg = SplErrorStrings.messageNonBoolean(this, node.getExpr().getType().getValue().prettyPrint());
      error(msg, node.get_SourcePositionStart());

    }

  }

}
