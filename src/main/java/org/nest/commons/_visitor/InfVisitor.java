package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;

import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * @author ptraeder
 */
public class InfVisitor implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.value(getRealType()));
  }
}
