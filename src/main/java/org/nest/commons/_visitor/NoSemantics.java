package org.nest.commons._visitor;

import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;

import static org.nest.symboltable.predefined.PredefinedTypes.getIntegerType;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

/**
 * @author ptraeder
 */
public class NoSemantics implements CommonsVisitor {
  final String ERROR_CODE = "SPL_NO_SEMANTICS: ";

  @Override
  public void visit(ASTExpr expr) {
    final String errorMsg = ERROR_CODE+"Unable to derive type of: " + AstUtils.toString(expr);
    expr.setType(Either.error(errorMsg));
    warn(errorMsg,expr.get_SourcePositionStart());
  }
}
