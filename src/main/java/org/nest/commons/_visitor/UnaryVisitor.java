package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;

/**
 * @author ptraeder
 */
public class UnaryVisitor implements CommonsVisitor {
  final String ERROR_CODE = "NESTML_UNARY_VISITOR: ";

  //Expr = (unaryPlus:["+"] | unaryMinus:["-"] | unaryTilde:["~"]) term:Expr

  @Override
  public void visit(ASTExpr expr){
    final Either<TypeSymbol, String> termType  = expr.getTerm().get().getType();

    if(termType.isError()){
      expr.setType(termType);
      return;
    }

    if (expr.isUnaryMinus() || expr.isUnaryPlus()) {
      if (isNumeric(termType.getValue())) {
        expr.setType(termType);
        return;
      }
      else {
        final String errorMsg = ERROR_CODE+"Cannot perform an arithmetic operation on a non-numeric type";
        expr.setType(Either.error(errorMsg));
        error(errorMsg,expr.get_SourcePositionStart());
        return;
      }
    }
    else if (expr.isUnaryTilde()) {
        if (isInteger(termType.getValue())) {
          expr.setType(termType);
          return;
        }
        else {
          final String errorMsg = ERROR_CODE+"Cannot perform an arithmetic operation on a non-numeric type";
          expr.setType(Either.error(errorMsg));
          error(errorMsg,expr.get_SourcePositionStart());
          return;
        }
    }
    //Catch-all if no case has matched
    final String errorMsg = ERROR_CODE+"Cannot determine the type of the expression: " + AstUtils.toString(expr);
    error(errorMsg,expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
  }
}

