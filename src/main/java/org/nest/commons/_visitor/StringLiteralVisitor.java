package org.nest.commons._visitor;

import static org.nest.symboltable.predefined.PredefinedTypes.getStringType;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;

/**
 * @author ptraeder
 */
public class StringLiteralVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.value(getStringType()));
  }
}
