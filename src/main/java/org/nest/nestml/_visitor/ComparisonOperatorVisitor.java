package org.nest.nestml._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.TypeSymbol;

import static org.nest.nestml._symboltable.typechecking.TypeChecker.*;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class ComparisonOperatorVisitor implements NESTMLVisitor {

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsTypeE = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsTypeE = expr.getRight().get().getType();

    if (lhsTypeE.isError()) {
      expr.setType(lhsTypeE);
      return;
    }
    if (rhsTypeE.isError()) {
      expr.setType(rhsTypeE);
      return;
    }

    TypeSymbol lhsType = lhsTypeE.getValue();
    TypeSymbol rhsType = rhsTypeE.getValue();

    if (
        ((lhsType.equals(getRealType()) || lhsType.equals(getIntegerType())) &&
         (rhsType.equals(getRealType()) || rhsType.equals(getIntegerType()))) ||
        (lhsType.getName().equals(rhsType.getName()) && isNumeric(lhsType)) ||
        isBoolean(lhsType) && isBoolean(rhsType)) {
      expr.setType(Either.value(getBooleanType()));
      return;
    }

    //Error message for any other operation
    if ((isUnit(lhsType) && isNumeric(rhsType)) ||
        (isUnit(rhsType) && isNumeric(lhsType))) {
      final String errorMsg = CommonsErrorStrings.messageComparison(this, expr.get_SourcePositionStart());
      expr.setType(Either.value(getBooleanType()));
      Log.warn(errorMsg, expr.get_SourcePositionStart());
    }
    else {
      final String errorMsg = CommonsErrorStrings.messageNumeric(this, expr.get_SourcePositionStart());
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg, expr.get_SourcePositionStart());
    }

  }

}
