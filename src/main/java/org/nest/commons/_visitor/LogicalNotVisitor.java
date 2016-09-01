package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;



/**
 * @author ptraeder
 */
public class LogicalNotVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    checkState(expr.getExpr().get().getType().isPresent());
    final Either<TypeSymbol, String> exprType  = expr.getExpr().get().getType().get();

      if (exprType.isError()) {
        expr.setType(exprType);
        return;
      }
      else if (isBoolean(exprType.getValue())) {
        expr.setType(Either.value(getBooleanType()));
        return;
      }
      else {
        expr.setType(Either.error("Logical 'not' expects an boolean type and not: " + exprType.getValue()));
        return;
      }

  }
}
