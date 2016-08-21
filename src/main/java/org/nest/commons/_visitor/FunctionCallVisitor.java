package org.nest.commons._visitor;

import java.util.Optional;


import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.utils.NESTMLSymbols;

/**
 * @author ptraeder
 */
public class FunctionCallVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    final String functionName = expr.getFunctionCall().get().getCalleeName();

    final Optional<MethodSymbol> methodSymbol = NESTMLSymbols.resolveMethod(expr.getFunctionCall().get());
    if (!methodSymbol.isPresent()) {
      final String msg = "Cannot resolve the method: " + functionName;
      expr.setType(Either.error(msg));
      return;
    }

    if (new TypeChecker().checkVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = "Function "+functionName+" with returntype 'Void'"
          + " cannot be used in expressions. @"+expr.get_SourcePositionEnd();
      expr.setType(Either.error(errorMsg));
      return;
    }
    expr.setType(Either.value(methodSymbol.get().getReturnType()));
    return;
    }
}
