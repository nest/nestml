package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.*;
import static org.nest.symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class ComparisonOperatorVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_COMPARISON_OPERATOR_VISITOR";

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsTypeE = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsTypeE = expr.getRight().get().getType();

    if (lhsTypeE.isError()) {
      expr.setType(lhsTypeE);
      return;
    }
    if (rhsTypeE.isError()) {
      expr.setType(rhsTypeE);
      return;
    }

    TypeSymbol lhsType = lhsTypeE.getValue();
    TypeSymbol rhsType = rhsTypeE.getValue();

    if (
        ((lhsType.equals(getRealType()) || lhsType.equals(getIntegerType())) &&
        (rhsType.equals(getRealType()) || rhsType.equals(getIntegerType())))
            ||
        (lhsType.getName().equals(rhsType.getName()) && isNumeric(lhsType))
            ||
        isBoolean(lhsType) && isBoolean(rhsType)) {
      expr.setType(Either.value(getBooleanType()));
      return;
    }

    //Error message for any other operation
    if( (isUnit(lhsType)&&isNumeric(rhsType)) ||
    (isUnit(rhsType)&&isNumeric(lhsType)) ){
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +"SI types in comparison do not match.";
      expr.setType(Either.value(getBooleanType()));
      Log.warn(errorMsg,expr.get_SourcePositionStart());
    }else{
      final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +"Only numeric types can be compared.";
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg,expr.get_SourcePositionStart());
    }
  }

}
