package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.commons._visitor.ExpressionTypeVisitor.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isInteger;


/**
 * @author ptraeder
 */
public class UnaryVisitor implements CommonsVisitor {
  //Expr = (unaryPlus:["+"] | unaryMinus:["-"] | unaryTilde:["~"]) term:Expr

  @Override
  public void visit(ASTExpr expr){
    checkState(expr.getTerm().get().getType().isPresent());
    final Either<TypeSymbol, String> termType  = expr.getTerm().get().getType().get();

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
        String errorMsg = "Cannot perform an arithmetic operation on a non-numeric type";
        expr.setType(Either.error(errorMsg));
        return;
      }
    }
    else if (expr.isUnaryTilde()) {
        if (isInteger(termType.getValue())) {
          expr.setType(termType);
          return;
        }
        else {
          String errorMsg = "Cannot perform an arithmetic operation on a non-numeric type";
          expr.setType(Either.error(errorMsg));
          return;
        }
    }
    //Catch-all if no case has matched
    String msg = "Cannot determine the type of the Expression-Node @<"
        + expr.get_SourcePositionStart() + ", " + expr.get_SourcePositionEnd();
    expr.setType(Either.error(msg));
  }
}

