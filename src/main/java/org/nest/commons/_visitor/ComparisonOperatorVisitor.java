package org.nest.commons._visitor;

import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isNumeric;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isUnit;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getIntegerType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * @author ptraeder
 */
public class ComparisonOperatorVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_COMPARISON_OPERATOR_VISITOR: ";

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType();

    if (lhsType.isError()) {
      expr.setType(lhsType);
      return;
    }
    if (rhsType.isError()) {
      expr.setType(rhsType);
      return;
    }

    if (
        ((lhsType.getValue().equals(getRealType()) || lhsType.getValue().equals(getIntegerType())) &&
        (rhsType.getValue().equals(getRealType()) || rhsType.getValue().equals(getIntegerType())))
            ||
        (lhsType.getValue().getName().equals(rhsType.getValue().getName()) && isNumeric(lhsType.getValue()))
            ||
        isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
      expr.setType(Either.value(getBooleanType()));
      return;
    }

    //Error message for any other operation
    if( (isUnit(lhsType.getValue())&&isNumeric(rhsType.getValue())) ||
    (isUnit(rhsType.getValue())&&isNumeric(lhsType.getValue())) ){
      final String errorMsg = ERROR_CODE+"\""+AstUtils.toString(expr)+"\" - SI types in comparison do not match.";
      expr.setType(Either.value(getBooleanType()));
      Log.warn(errorMsg,expr.get_SourcePositionStart());
    }else{
      final String errorMsg = ERROR_CODE+"\""+AstUtils.toString(expr)+"\" - Only numeric types can be compared.";
      expr.setType(Either.error(errorMsg));
      Log.error(errorMsg,expr.get_SourcePositionStart());
    }
  }

}
