package org.nest.commons._visitor;

import static com.google.common.base.Preconditions.checkState;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

/**
 * @author ptraeder
 */
public class ParenthesesVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    checkState(expr.getExpr().get().getType().isPresent());
    final Either<TypeSymbol, String> exprType  = expr.getExpr().get().getType().get();
      expr.setType(exprType);
  }
}
