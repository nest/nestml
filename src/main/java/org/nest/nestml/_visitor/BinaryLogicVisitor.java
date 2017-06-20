package org.nest.nestml._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.TypeSymbol;

import static org.nest.nestml._symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getBooleanType;


/**
 * @author ptraeder
 */
public class BinaryLogicVisitor implements NESTMLVisitor {

  @Override
  public void visit(final ASTExpr expr) {
    // both elements are there by construction
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType();

    if (lhsType.isError()) {
      expr.setType(lhsType);
      return;
    }
    if (rhsType.isError()) {
      expr.setType(rhsType);
      return;
    }

    if (isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
      expr.setType(Either.value(getBooleanType()));
    }
    else {
      final String errorMsg = CommonsErrorStrings.message(this, expr.get_SourcePositionStart());
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg, expr.get_SourcePositionStart());
    }

  }

}
