package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.commons._visitor.ExpressionTypeVisitor.*;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr){
    final Either<TypeSymbol, String> baseType = expr.getBase().get().getType();
    final Either<TypeSymbol, String> exponentType = expr.getExponent().get().getType();

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
      else if (isUnit(baseType.getValue())) {
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
    String msg = "Cannot determine the type of the expression: " + AstUtils.toString(expr);
    expr.setType(Either.error(msg));
  }
}
