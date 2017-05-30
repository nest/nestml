package org.nest.nestml._visitor;

import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;

import static org.nest.nestml._symboltable.predefined.PredefinedTypes.getBooleanType;


/**
 * @author ptraeder
 */
public class BooleanLiteralVisitor implements NESTMLVisitor {

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.value(getBooleanType()));
  }
}
