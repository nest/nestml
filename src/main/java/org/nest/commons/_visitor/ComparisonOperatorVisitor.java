package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.commons._visitor.ExpressionTypeVisitor.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;


/**
 * @author ptraeder
 */
public class ComparisonOperatorVisitor implements CommonsVisitor{

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

    if (isNumeric(lhsType.getValue()) && isNumeric(rhsType.getValue()) ||
        isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
      expr.setType(Either.value(getBooleanType()));
      return;
    }

    //Error message specific to equals
    if (expr.isEq() ) {
      final String errorMsg = "Only expressions of the same type can be checked for equality. And not: " +
          lhsType.getValue() + " and " + rhsType.getValue();
      expr.setType(Either.error(errorMsg));
      return;
    }

    //Error message for any other operation
    final String errorMsg = "This operation expects both operands of a numeric type.";
    expr.setType(Either.error(errorMsg));
  }

}
