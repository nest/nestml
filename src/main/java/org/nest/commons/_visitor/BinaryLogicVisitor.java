package org.nest.commons._visitor;

import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static com.google.common.base.Preconditions.checkState;


/**
 * @author ptraeder
 */
public class BinaryLogicVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    checkState(expr.getLeft().get().getType().isPresent());
    checkState(expr.getRight().get().getType().isPresent());
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType().get();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType().get();

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
      return;
    }
    else {
      final String errorMsg = "Both operands of the logical expression must be boolean ";
      expr.setType(Either.error(errorMsg));
    }

  }
}
