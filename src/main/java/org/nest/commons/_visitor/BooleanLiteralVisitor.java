package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;

import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;


/**
 * @author ptraeder
 */
public class BooleanLiteralVisitor implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.value(getBooleanType()));
  }
}
