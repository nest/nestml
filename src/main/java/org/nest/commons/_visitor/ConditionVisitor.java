package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;

/**
 *  @author ptraeder
 * */
public class ConditionVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    if (expr.getCondition().isPresent()) {
      checkState(expr.getCondition().get().getType().isPresent());
      checkState(expr.getIfTrue().get().getType().isPresent());
      checkState(expr.getIfNot().get().getType().isPresent());
      final Either<TypeSymbol, String> condition = expr.getCondition().get().getType().get();
      final Either<TypeSymbol, String> ifTrue = expr.getIfTrue().get().getType().get();
      final Either<TypeSymbol, String> ifNot = expr.getIfNot().get().getType().get();

      if (condition.isError()) {
        expr.setType(condition);
        return;
      }
      if (ifTrue.isError()) {
        expr.setType(ifTrue);
        return;
      }
      if (ifNot.isError()) {
        expr.setType(ifNot);
        return;
      }

      if (!condition.getValue().equals(getBooleanType())) {
        expr.setType(Either.error("The ternary operator condition must be a boolean: " + AstUtils.toString(expr) + ".  And not a: " + condition.getValue()));
        return;
      }
      if (!isCompatible(ifTrue.getValue(), (ifNot.getValue()))) {
        expr.setType(Either.error("The ternary operator results must be of the same type: " + AstUtils.toString(expr) + ".  And not: " + ifTrue.getValue() + " and " + ifNot.getValue()));
        return;
      }
      expr.setType(ifTrue);
      return;
    }
  }
}
