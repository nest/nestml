package org.nest.commons._visitor;

import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.units.unitrepresentation.UnitRepresentation;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
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
          final String errorMsg = CommonsErrorStrings.messageUnitBase(this, expr.get_SourcePositionStart());
          expr.setType(Either.error(errorMsg));
          error(errorMsg, expr.get_SourcePositionStart());
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
          error(errorMsg, expr.get_SourcePositionStart());
          return;
        }
      }
      else {
        expr.setType(Either.value(getRealType()));
        return;
      }
    }

    //Catch-all if no case has matched
    final String errorMsg = CommonsErrorStrings.messageType(
        this,
        baseType.prettyPrint(),
        exponentType.prettyPrint(),
        expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    error(errorMsg, expr.get_SourcePositionStart());
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
        return Either.error(CommonsErrorStrings.messageFloatingPointExponent(this, expr.get_SourcePositionStart()));
      }

    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericValue(expr.getTerm().get());
      if (term.isError()) {
        return term;
      }
      return Either.value(-term.getValue());
    }

    return Either.error(CommonsErrorStrings.messageNonConstantExponent(this, expr.get_SourcePositionStart()));
  }

}

