package org.nest.nestml._visitor;

import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.warn;

/**
 * @author ptraeder
 */
public class NoSemantics implements NESTMLVisitor {


  @Override
  public void visit(ASTExpr expr) {
    final String errorMsg = CommonsErrorStrings.message(this, AstUtils.toString(expr), expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    warn(errorMsg, expr.get_SourcePositionStart());
  }

}
