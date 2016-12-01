package org.nest.commons._visitor;

import static de.se_rwth.commons.logging.Log.error;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

/**
 * @author ptraeder
 */
public class NoSemantics implements CommonsVisitor {
  final String ERROR_CODE = "NESTML_NO_SEMANTICS: ";

  @Override
  public void visit(ASTExpr expr) {
    final String errorMsg = ERROR_CODE+"Unable to derive type of: " + AstUtils.toString(expr);
    expr.setType(Either.error(errorMsg));
    error(errorMsg,expr.get_SourcePositionStart());
  }
}
