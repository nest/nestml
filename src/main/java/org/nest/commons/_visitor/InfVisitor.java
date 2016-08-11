package org.nest.commons._visitor;

import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;

/**
 * @author ptraeder
 */
public class InfVisitor  implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.value(getRealType()));
  }
}
