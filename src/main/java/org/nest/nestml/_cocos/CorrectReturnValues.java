/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.spl._ast.ASTReturnStmt;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.ASTUtils;

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
  CocoErrorStrings errorStrings = CocoErrorStrings.getInstance();

  public void check(final ASTFunction fun) {
    checkState(fun.getEnclosingScope().isPresent(),
        "Function: " + fun.getName() + " has no scope assigned. ");
    final Scope scope = fun.getEnclosingScope().get();
    // get return type
    final Optional<MethodSymbol> mEntry = scope.resolve(fun.getName(), MethodSymbol.KIND);
    checkState(mEntry.isPresent(), "Cannot resolve the method: " + fun.getName());
    final TypeSymbol functionReturnType = mEntry.get().getReturnType();

    // get all return statements in block
    final List<ASTReturnStmt> returns = ASTUtils.getReturnStatements(fun.getBlock());

    final TypeChecker tc = new TypeChecker();

    for (ASTReturnStmt r : returns) {
      // no return expression
      if (!r.getExpr().isPresent() && !tc.checkVoid(functionReturnType)) {
        // void return value
        final String msg = errorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

       error(msg, r.get_SourcePositionStart());

      }

      if (r.getExpr().isPresent()) {

        final Either<TypeSymbol, String> returnExpressionType
            = typeCalculator.computeType(r.getExpr().get());
        if (returnExpressionType.isRight()) {
          final String msg = errorStrings.getErrorMsgCannotDetermineExpressionType(this);

          Log.warn(msg, r.getExpr().get().get_SourcePositionStart());
          return;
        }

        if (functionReturnType.getName() == returnExpressionType.getLeft().get().getName() ||
            TypeChecker.isCompatible(functionReturnType, returnExpressionType.getLeft().get())) {
          return;
        }

        if (tc.checkVoid(functionReturnType) && !tc.checkVoid(returnExpressionType.getLeft().get())) {
          // should return nothing, but does not
          final String msg = errorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

         error(msg, r.get_SourcePositionStart());
        }

        // same type is ok (e.g. string, boolean,integer, real,...)
        if (tc.checkString(functionReturnType) && !tc.checkString(returnExpressionType.getLeft().get())) {
          // should return string, but does not
          final String msg = errorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

         error(msg, r.get_SourcePositionStart());
        }

        if (tc.isBoolean(functionReturnType) && !tc.isBoolean(returnExpressionType.getLeft().get())) {
          // should return bool, but does not
          final String msg = errorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

         error(msg, r.get_SourcePositionStart());
        }

        if (tc.checkUnit(functionReturnType) && !tc.checkUnit(returnExpressionType.getLeft().get())) {
          // should return numeric, but does not
          final String msg = errorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

         error(msg, r.get_SourcePositionStart());
        }

        // real rType and integer eType is ok, since more general
        // integer rType and real eType is not ok
        final String msg = errorStrings.getErrorMsgCannotConvertReturnValue(this,returnExpressionType.getLeft().get().getName(),functionReturnType.getName());

       error(msg, r.get_SourcePositionStart());
      }

    }

  }

}
