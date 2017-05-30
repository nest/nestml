/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTReturnStmt;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.typechecking.TypeChecker;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static de.se_rwth.commons.logging.Log.warn;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isString;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.isVoid;

/**
 * The type of all return expression must conform to the declaration type.
 *
 * @author ippen, plotnikov
 */
public class FunctionReturnsIncorrectValue implements NESTMLASTFunctionCoCo {

  public void check(final ASTFunction fun) {
    checkState(fun.getEnclosingScope().isPresent(), "Function: " + fun.getName() + " has no scope assigned. ");
    final Scope scope = fun.getEnclosingScope().get();
    // get return type
    final Optional<MethodSymbol> mEntry = scope.resolve(fun.getName(), MethodSymbol.KIND);
    checkState(mEntry.isPresent(), "Cannot resolve the method: " + fun.getName());
    final TypeSymbol functionReturnType = mEntry.get().getReturnType();

    // get all return statements in block
    final List<ASTReturnStmt> returns = AstUtils.getReturnStatements(fun.getBlock());

    for (ASTReturnStmt r : returns) {
      // no return expression
      if (!r.getExpr().isPresent() && !isVoid(functionReturnType)) {
        // void return value
        final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.getName());

       error(msg, r.get_SourcePositionStart());

      }

      if (r.getExpr().isPresent()) {

        final Either<TypeSymbol, String> returnExpressionType = r.getExpr().get().getType();
        if (returnExpressionType.isError()) {
          final String msg = NestmlErrorStrings.getErrorMsgCannotDetermineExpressionType(this);

          warn(msg, r.getExpr().get().get_SourcePositionStart());
          return;
        }

        if (functionReturnType.getName().equals( returnExpressionType.getValue().getName()) ||
            TypeChecker.isCompatible(functionReturnType, returnExpressionType.getValue())) {
          return;
        }

        if (isVoid(functionReturnType) && !isVoid(returnExpressionType.getValue())) {
          // should return nothing, but does not
          final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.prettyPrint());

         error(msg, r.get_SourcePositionStart());
        }

        // same type is ok (e.g. string, boolean,integer, real,...)
        if (isString(functionReturnType) && !isString(returnExpressionType.getValue())) {
          // should return string, but does not
          final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.prettyPrint());

         error(msg, r.get_SourcePositionStart());
        }

        if (TypeChecker.isBoolean(functionReturnType) && !TypeChecker.isBoolean(returnExpressionType.getValue())) {
          // should return bool, but does not
          final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.prettyPrint());

         error(msg, r.get_SourcePositionStart());
        }

        if (TypeChecker.isUnit(functionReturnType) && !TypeChecker.isUnit(returnExpressionType.getValue())) {
          // should return unit, but does not
          final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.prettyPrint());

         warn(msg, r.get_SourcePositionStart());
        }

        if (TypeChecker.isInteger(functionReturnType) && TypeChecker.isReal(returnExpressionType.getValue())) {
          // integer rType and real eType is not ok
          final String msg = NestmlErrorStrings.getErrorMsgWrongReturnType(this,fun.getName(),functionReturnType.prettyPrint());

          error(msg, r.get_SourcePositionStart());
        }

        final String msg = NestmlErrorStrings.getErrorMsgCannotConvertReturnValue(this,returnExpressionType.getValue().getName(),functionReturnType.prettyPrint());
        if(TypeChecker.isUnit(functionReturnType)){
          warn(msg, r.get_SourcePositionStart());
        }else{
          error(msg, r.get_SourcePositionStart());
        }

      }

    }

  }

}
