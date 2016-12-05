/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.NESTMLSymbols;

import java.util.Optional;

/**
 * Checks all function calls in an expression. For a not-void methods returns just its return type. For a void methods,
 * reports an error.
 *
 * @author plotnikov, ptraeder
 */
public class FunctionCallVisitor implements CommonsVisitor {
  final String ERROR_CODE = "SPL_FUNCTION_CALL_VISITOR: ";

  @Override
  public void visit(final ASTExpr expr) {
    final String functionName = expr.getFunctionCall().get().getCalleeName();

    final Optional<MethodSymbol> methodSymbol = NESTMLSymbols.resolveMethod(expr.getFunctionCall().get());

    if (!methodSymbol.isPresent()) {
      final String errorMsg = ERROR_CODE+"Cannot resolve the method: " + functionName;
      expr.setType(Either.error(errorMsg));
      return;
    }

    if (TypeChecker.checkVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = ERROR_CODE+"Function " + functionName + " with the return-type 'Void'"
                              + " cannot be used in expressions. @" + expr.get_SourcePositionEnd();
      expr.setType(Either.error(errorMsg));
      return;
    }
    expr.setType(Either.value(methodSymbol.get().getReturnType()));
  }

}
