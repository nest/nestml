/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.symboltable.typechecking.Either;
import org.nest.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.NestmlSymbols;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.units._cocos.UnitsErrorStrings;
import org.nest.utils.AstUtils;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;

/**
 * Checks all function calls in an expression. For a not-void methods returns just its return type. For a void methods,
 * reports an error.
 *
 * @author plotnikov, ptraeder
 */
public class FunctionCallVisitor implements CommonsVisitor {

  @Override
  public void visit(final ASTExpr expr) { // visits only function calls
    checkState(expr.getFunctionCall().isPresent());
    final String functionName = expr.getFunctionCall().get().getCalleeName();

    final Optional<MethodSymbol> methodSymbol = NestmlSymbols.resolveMethod(expr.getFunctionCall().get());

    if (!methodSymbol.isPresent()) {
      final String errorMsg = AstUtils.print(expr.get_SourcePositionStart()) + " : " + "Cannot resolve the method: " + functionName;
      expr.setType(Either.error(errorMsg));
      return;
    }

    if (TypeChecker.isVoid(methodSymbol.get().getReturnType())) {
      final String errorMsg = UnitsErrorStrings.message(this, functionName);
      expr.setType(Either.error(errorMsg));
      return;
    }
    expr.setType(Either.value(methodSymbol.get().getReturnType()));
  }

}
