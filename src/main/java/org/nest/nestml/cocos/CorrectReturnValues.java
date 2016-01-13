/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.spl._ast.ASTReturnStmt;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTNodes;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * The type of the return expression must conform to the declaration type.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class CorrectReturnValues implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "SPL_CORRECT_RETURN_VALUES";
  private final ExpressionTypeCalculator typeCalculator = new ExpressionTypeCalculator();

  public void check(final ASTFunction fun) {
    checkState(fun.getEnclosingScope().isPresent(),
        "Function: " + fun.getName() + " has no scope assigned. ");
    final Scope scope = fun.getEnclosingScope().get();
    // get return type
    final Optional<MethodSymbol> mEntry = scope.resolve(fun.getName(), MethodSymbol.KIND);
    checkState(mEntry.isPresent(), "Cannot resolve the method: " + fun.getName());
    final TypeSymbol functionReturnType = mEntry.get().getReturnType();

    // get all return statements in block
    final List<ASTReturnStmt> returns = ASTNodes.getReturnStatements(fun.getBlock());

    final TypeChecker tc = new TypeChecker();

    for (ASTReturnStmt r : returns) {
      // no return expression
      if (!r.getExpr().isPresent() && !tc.checkVoid(functionReturnType)) {
        // void return value
        final String msg = "Function '" + fun.getName() + "' must return a result of type "
            + functionReturnType.getName() + ".";
       error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());

      }

      if (r.getExpr().isPresent()) {

        final Either<TypeSymbol, String> returnExpressionType
            = typeCalculator.computeType(r.getExpr().get());
        if (returnExpressionType.isRight()) {
          Log.warn(ERROR_CODE + "Cannot determine the type of the expression", r.getExpr().get().get_SourcePositionStart());
          return;
        }

        if (functionReturnType.getName() == returnExpressionType.getLeft().get().getName() ||
            TypeChecker.isCompatible(functionReturnType, returnExpressionType.getLeft().get())) {
          return;
        }

        if (tc.checkVoid(functionReturnType) && !tc.checkVoid(returnExpressionType.getLeft().get())) {
          // should return nothing, but does not
          final String msg = "Function '" + fun.getName() + "' must not return a result."
              + functionReturnType.getName() + ".";
         error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());
        }

        // same type is ok (e.g. string, boolean,integer, real,...)
        if (tc.checkString(functionReturnType) && !tc.checkString(returnExpressionType.getLeft().get())) {
          // should return string, but does not
          final String msg = "Function '" + fun.getName() + "' must return a result of type "
              + functionReturnType.getName() + ".";
         error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());
        }

        if (tc.checkBoolean(functionReturnType) && !tc.checkBoolean(returnExpressionType.getLeft().get())) {
          // should return bool, but does not
          final String msg = "Function '" + fun.getName() + "' must return a result of type "
              + functionReturnType.getName() + ".";
         error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());
        }

        if (tc.checkUnit(functionReturnType) && !tc.checkUnit(returnExpressionType.getLeft().get())) {
          // should return numeric, but does not
          final String msg = "Function '" + fun.getName() + "' must return a result of type "
              + functionReturnType.getName() + ".";
         error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());
        }

        // real rType and integer eType is ok, since more general
        // integer rType and real eType is not ok
        final String msg = "Cannot convert from " + returnExpressionType.getLeft().get().getName()
            + " (type of return expression) to " + functionReturnType.getName()
            + " (return type), since the first is real domain and the second is in the integer "
            + "domain and conversion reduces the precision.";
       error(ERROR_CODE + ":" +  msg, r.get_SourcePositionStart());
      }

    }

  }

}
