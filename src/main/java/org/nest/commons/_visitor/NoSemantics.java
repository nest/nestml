package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

/**
 * @author ptraeder
 */
public class NoSemantics implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
    expr.setType(Either.error("Unable to derive type of: " + AstUtils.toString(expr)));
  }
}
