package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.commons._visitor.ExpressionTypeVisitor.calculateNumericValue;
import static org.nest.commons._visitor.ExpressionTypeVisitor.handleDefaultError;
import static org.nest.commons._visitor.ExpressionTypeVisitor.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr){
    checkState(expr.getBase().get().getType().isPresent());
    checkState(expr.getExponent().get().getType().isPresent());
    final Either<TypeSymbol, String> baseType = expr.getBase().get().getType().get();
    final Either<TypeSymbol, String> exponentType = expr.getExponent().get().getType().get();

    if (baseType.isError()) {
      expr.setType(baseType);
      return;
    }
    if (exponentType.isError()) {
      expr.setType(exponentType);
      return;
    }
    else if (isNumeric(baseType.getValue()) && isNumeric(exponentType.getValue())) {
      if (isInteger(baseType.getValue()) && isInteger(exponentType.getValue())) {
        expr.setType(Either.value(getIntegerType()));
        return;
      }
      else if (checkUnit(baseType.getValue())) {
        if (!isInteger(exponentType.getValue())) {
          expr.setType(Either.error("With a Unit base, the exponent must be an Integer!"));
          return;
        }
        UnitRepresentation baseRep = new UnitRepresentation(baseType.getValue().getName());
        Either<Integer, String> numericValue = calculateNumericValue(expr.getExponent().get());//calculate exponent value if exponent composed of literals
        if (numericValue.isValue()) {
          expr.setType(Either.value(getTypeIfExists((baseRep.pow(numericValue.getValue())).serialize()).get()));
          return;
        }
        else {
          expr.setType(Either.error(numericValue.getError()));
          return;
        }
      }
      else {
        expr.setType(Either.value(getRealType()));
        return;
      }
    }
    //Catch-all if no case has matched
    handleDefaultError(expr);
  }
}
