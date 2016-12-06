package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static org.nest.commons._visitor.ExpressionTypeVisitor.*;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_POW_VISITOR";

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
          final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
              "With a Unit base, the exponent must be an integer.";
          expr.setType(Either.error(errorMsg));
          error(errorMsg,expr.get_SourcePositionStart());
          return;
        }
        UnitRepresentation baseRep = new UnitRepresentation(baseType.getValue().getName());
        Either<Integer, String> numericValue = calculateNumericValue(expr.getExponent().get());//calculate exponent value if exponent composed of literals
        if (numericValue.isValue()) {
          expr.setType(Either.value(getTypeIfExists((baseRep.pow(numericValue.getValue())).serialize()).get()));
          return;
        }
        else {
          final String errorMsg = numericValue.getError();
          expr.setType(Either.error(errorMsg));
          error(errorMsg,expr.get_SourcePositionStart());
          return;
        }
      }
      else {
        expr.setType(Either.value(getRealType()));
        return;
      }
    }
    //Catch-all if no case has matched
    final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
        "Cannot determine the type of the expression: " + baseType.getValue().prettyPrint()
        +"**"+exponentType.getValue().prettyPrint();
    expr.setType(Either.error(errorMsg));
    error(errorMsg,expr.get_SourcePositionStart());
  }


  public Either<Integer, String> calculateNumericValue(ASTExpr expr) {
    if (expr.isLeftParentheses()) {
      return calculateNumericValue(expr.getExpr().get());
    }
    else if (expr.getNESTMLNumericLiteral().isPresent()) {
      if (expr.getNESTMLNumericLiteral().get().getNumericLiteral() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNESTMLNumericLiteral().get().getNumericLiteral();
        return Either.value(literal.getValue());
      }
      else {
        return Either.error(ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
            "No floating point values allowed in the exponent to a UNIT base");
      }
    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericValue(expr.getTerm().get());
      if (term.isError()) {
        return term;
      }
      return Either.value(-term.getValue());
    }

    return Either.error(ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
        "Cannot calculate value of exponent. Must be a static value!");
  }
}

