package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_POW_VISITOR";

  @Override
  public void visit(ASTExpr expr){
    final Either<TypeSymbol, String> baseTypeE = expr.getBase().get().getType();
    final Either<TypeSymbol, String> exponentTypeE = expr.getExponent().get().getType();

    if (baseTypeE.isError()) {
      expr.setType(baseTypeE);
      return;
    }
    if (exponentTypeE.isError()) {
      expr.setType(exponentTypeE);
      return;
    }

    TypeSymbol baseType = baseTypeE.getValue();
    TypeSymbol exponentType = exponentTypeE.getValue();

    if (isNumeric(baseType) && isNumeric(exponentType)) {
      if (isInteger(baseType) && isInteger(exponentType)) {
        expr.setType(Either.value(getIntegerType()));
        return;
      }
      else if (isUnit(baseType)) {
        if (!isInteger(exponentType)) {
          final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
              "With a Unit base, the exponent must be an integer.";
          expr.setType(Either.error(errorMsg));
          error(errorMsg,expr.get_SourcePositionStart());
          return;
        }
        UnitRepresentation baseRep = UnitRepresentation.getBuilder().serialization(baseType.getName()).build();
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
        "Cannot determine the type of the expression: " + baseType.prettyPrint()
        +"**"+exponentType.prettyPrint();
    expr.setType(Either.error(errorMsg));
    error(errorMsg,expr.get_SourcePositionStart());
  }


  public Either<Integer, String> calculateNumericValue(ASTExpr expr) {
    //TODO write tests for this
    if (expr.isLeftParentheses()) {
      return calculateNumericValue(expr.getExpr().get());
    }
    else if (expr.getNumericLiteral().isPresent()) {
      if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNumericLiteral().get();
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

