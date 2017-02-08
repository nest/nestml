package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.warn;

/**
 * @author ptraeder
 */
public class NoSemantics implements CommonsVisitor {
  final String ERROR_CODE = "SPL_NO_SEMANTICS";

  @Override
  public void visit(ASTExpr expr) {
    final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
        "This expression is not implemented: " + AstUtils.toString(expr);
    expr.setType(Either.error(errorMsg));
    warn(errorMsg, expr.get_SourcePositionStart());
  }

}
