package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;


/**
 * @author ptraeder
 */
public class BinaryLogicVisitor implements CommonsVisitor {

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
