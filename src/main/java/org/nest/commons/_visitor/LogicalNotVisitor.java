package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;



/**
 * @author ptraeder
 */
public class LogicalNotVisitor implements CommonsVisitor{
  final String ERROR_CODE = "SPL_LOGICAL_NOT_VISITOR";
  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> exprType  = expr.getExpr().get().getType();

      if (exprType.isError()) {
        expr.setType(exprType);
        return;
      }
      else if (isBoolean(exprType.getValue())) {
        expr.setType(Either.value(getBooleanType()));
        return;
      }
      else {
        final String errorMsg = ERROR_CODE+ " " + AstUtils.print(expr.get_SourcePositionStart()) + " : " +
            "Logical 'not' expects an boolean type and not: " + exprType.getValue();
        expr.setType(Either.error(errorMsg));
        error(errorMsg,expr.get_SourcePositionStart());
        return;
      }

  }
}
