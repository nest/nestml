package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.warn;

/**
 * @author ptraeder
 */
public class NoSemantics implements CommonsVisitor {


  @Override
  public void visit(ASTExpr expr) {
    final String errorMsg = CommonsErrorStrings.message(this, AstUtils.toString(expr), expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    warn(errorMsg, expr.get_SourcePositionStart());
  }

}
