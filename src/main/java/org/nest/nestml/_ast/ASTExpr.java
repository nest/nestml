/*
 * ASTExpr.java
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

package org.nest.nestml._ast;

import de.monticore.literals.literals._ast.ASTBooleanLiteral;
import de.monticore.literals.literals._ast.ASTNumericLiteral;
import de.monticore.literals.literals._ast.ASTStringLiteral;
import org.nest.nestml._visitor.ExpressionTypeVisitor;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;

import java.util.Optional;

/**
 * HW extension of the AST class. Provides method to compute the Expression type.
 *
 * @author ptraeder
 */
public class ASTExpr extends ASTExprTOP {

  private Optional<Either<TypeSymbol,String>> type = Optional.empty();

  private void doComputeType() {
//    checkArgument(getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");

    if(!type.isPresent()){
      //no type set yet. Run Visitor.
      ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
      accept(expressionTypeVisitor);
    }

    //Just to be sure. Should never happen
    if(!type.isPresent()){
      final String errorMsg = "This operation for expressions is not supported yet.";
      type= Optional.of(Either.error(errorMsg));
    }

    //Handle unitless expressions by returning real type instead
    if(type.get().isValue()){
      TypeSymbol typeSymbol = type.get().getValue();
      if(typeSymbol.getType() == TypeSymbol.Type.UNIT){
        UnitRepresentation unit = UnitRepresentation.getBuilder().serialization(typeSymbol.getName()).build();
        if(unit.isZero()){
         type =Optional.of(Either.value(PredefinedTypes.getRealType()));
        }
      }
    }
  }
  public Either<TypeSymbol,String> getType(){
    if(!type.isPresent()) {
      doComputeType();
    }
    return type.get();
  }

  public void setType(Either<TypeSymbol,String> type) {
    this.type = Optional.of(type);
  }

  public ASTExpr(){}

  public ASTExpr(ASTExpr base,
  ASTExpr exponent,
  ASTExpr term,
  ASTExpr expr,
  ASTExpr left,
  ASTExpr right,
  ASTExpr condition,
  ASTExpr ifTrue,
  ASTExpr ifNot,
  ASTFunctionCall functionCall,
  ASTBooleanLiteral booleanLiteral,
  ASTNumericLiteral numericLiteral,
  ASTStringLiteral stringLiteral,
  ASTVariable variable,
  boolean inf,
  boolean logicalOr,
  boolean logicalAnd,
  boolean logicalNot,
  boolean gt,
  boolean ge,
  boolean ne2,
  boolean ne,
  boolean eq,
  boolean le,
  boolean lt,
  boolean bitOr,
  boolean bitXor,
  boolean bitAnd,
  boolean shiftRight,
  boolean shiftLeft,
  boolean minusOp,
  boolean plusOp,
  boolean moduloOp,
  boolean divOp,
  boolean timesOp,
  boolean unaryTilde,
  boolean unaryMinus,
  boolean unaryPlus,
  boolean pow,
  boolean leftParentheses,
  boolean rightParentheses)  {

    super(base,exponent,term,expr,left,right,condition,ifTrue,ifNot,functionCall,booleanLiteral,numericLiteral,stringLiteral,
        variable,inf,logicalOr,logicalAnd,logicalNot,gt,ge,ne2,ne,eq,le,lt,bitOr,bitXor,bitAnd,shiftRight,shiftLeft,minusOp,
        plusOp,moduloOp,divOp,timesOp,unaryTilde,unaryMinus,unaryPlus,pow,leftParentheses,rightParentheses);
  }


}
