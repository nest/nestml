/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import org.nest.commons._ast.ASTExpr;
import org.nest.commons._visitor.ExpressionTypeVisitor;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.symboltable.predefined.PredefinedTypes;

import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;


/**
 * Compute the type of an expression by an recursive algorithm.
 *
 * @author plotnikov
 */
public class ExpressionTypeCalculator {

  public Either<TypeSymbol, String> computeType(final ASTExpr expr) {
    checkNotNull(expr);
    checkArgument(expr.getEnclosingScope().isPresent(), "No scope assigned. Please, run symboltable creator.");


    if(!expr.getType().isPresent()){
    //no type set yet. Run Visitor.
      ExpressionTypeVisitor expressionTypeVisitor = new ExpressionTypeVisitor();
      expressionTypeVisitor.handle(expr);
    }

    //Just to be sure. Should never happen
    if(!expr.getType().isPresent()){
      final String errorMsg = "This operation for expressions is not supported yet.";
      return Either.error(errorMsg);
    }

    //Handle unitless expressions by returning real type instead
    if(expr.getType().get().isValue()){
      TypeSymbol typeSymbol = expr.getType().get().getValue();
      if(typeSymbol.getType() == TypeSymbol.Type.UNIT){
        UnitRepresentation unit = new UnitRepresentation(typeSymbol.getName());
        if(unit.isZero()){
          expr.setType(Either.value(PredefinedTypes.getRealType()));
        }
      }
    }

    return expr.getType().get();
  }
}

