package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.symboltable.typechecking.TypeChecker.isNumeric;

/**
 * Expr = (unaryPlus:["+"] | unaryMinus:["-"] | unaryTilde:["~"]) term:Expr
 *
 * @author ptraeder
 */
public class UnaryVisitor implements CommonsVisitor {

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> termTypeE = expr.getTerm().get().getType();

    if (termTypeE.isError()) {
      expr.setType(termTypeE);
      return;
    }

    TypeSymbol termType = termTypeE.getValue();

    if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      if (isNumeric(termType)) {
        expr.setType(Either.value(termType));
        return;
      }
      else {
        final String errorMsg = CommonsErrorStrings.messageNonNumericType(
            this,
            termType.prettyPrint(),
            expr.get_SourcePositionStart());
        expr.setType(Either.error(errorMsg));
        error(errorMsg, expr.get_SourcePositionStart());
        return;
      }
    }
    else if (expr.isUnaryTilde()) {
      if (isInteger(termType)) {
        expr.setType(Either.value(termType));
        return;
      }
      else {
        final String errorMsg = CommonsErrorStrings.messageNonNumericType(
            this,
            termType.prettyPrint(),
            expr.get_SourcePositionStart());
        expr.setType(Either.error(errorMsg));
        error(errorMsg, expr.get_SourcePositionStart());
        return;
      }
    }
    //Catch-all if no case has matched
    final String errorMsg = CommonsErrorStrings.messageTypeError(
        this,
        AstUtils.toString(expr),
        expr.get_SourcePositionStart());
    error(errorMsg, expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
  }

}

