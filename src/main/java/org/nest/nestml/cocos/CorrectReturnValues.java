package org.nest.nestml.cocos;

import com.google.common.base.Preconditions;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.spl._ast.ASTReturnStmt;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.spl.symboltable.typechecking.TypeChecker;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.ASTNodes;

import java.util.List;
import java.util.Optional;

public class CorrectReturnValues implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "SPL_CORRECT_RETURN_VALUES";

  private final PredefinedTypesFactory predefinedTypesFactory;

  public CorrectReturnValues(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  public void check(final ASTFunction fun) {
    Preconditions.checkState(fun.getEnclosingScope().isPresent(),
        "Function: " + fun.getName() + " has no scope assigned. ");
    final Scope scope = fun.getEnclosingScope().get();
    // get return type
    final Optional<NESTMLMethodSymbol> mEntry = scope.resolve(fun.getName(), NESTMLMethodSymbol.KIND);
    Preconditions.checkState(mEntry.isPresent(), "Cannot resolve the method: " + fun.getName());
    final NESTMLTypeSymbol functionReturnType = mEntry.get().getReturnType();

    // get all return statements in block
    final List<ASTReturnStmt> returns = ASTNodes.getReturnStatements(fun.getBlock());

    final TypeChecker tc = new TypeChecker(predefinedTypesFactory);

    for (ASTReturnStmt r : returns) {
      // no return expression
      if (r.getExpr().isPresent() && !tc.checkVoid(functionReturnType)) {
        // void return value
        final String msg = "Function '" + fun.getName()
            + "' must return a result of type "
            + functionReturnType.getName() + ".";
        CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());

      }

      if (r.getExpr().isPresent()) {
        final ExpressionTypeCalculator typeCalculator = new ExpressionTypeCalculator(
            predefinedTypesFactory);
        final NESTMLTypeSymbol returnExpressionType = typeCalculator.computeType(r.getExpr().get());

        if (tc.checkVoid(functionReturnType) && !tc.checkVoid(returnExpressionType)) {
          // should return nothing, but does not
          final String msg = "Function '" + fun.getName()
              + "' must not return a result."
              + functionReturnType.getName() + ".";
          CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());
        }
        // same type is ok (e.g. string, boolean,integer, real,...)
        if (tc.checkString(functionReturnType) && !tc.checkString(returnExpressionType)) {
          // should return string, but does not
          final String msg = "Function '" + fun.getName()
              + "' must return a result of type "
              + functionReturnType.getName() + ".";
          CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());
        }
        if (tc.checkBoolean(functionReturnType) && !tc.checkBoolean(returnExpressionType)) {
          // should return bool, but does not
          final String msg = "Function '" + fun.getName()
              + "' must return a result of type "
              + functionReturnType.getName() + ".";
          CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());
        }
        if (tc.checkUnit(functionReturnType) && !tc.checkUnit(returnExpressionType)) {
          // should return numeric, but does not
          final String msg = "Function '" + fun.getName()
              + "' must return a result of type "
              + functionReturnType.getName() + ".";
          CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());
        }
        // real rType and integer eType is ok, since more general
        // integer rType and real eType is not ok
        final String msg = "Cannot convert from "
            + returnExpressionType.getName()
            + " (type of return expression) to "
            + functionReturnType.getName()
            + " (return type), since the first is real "
            + "domain and the second is in the integer domain "
            + "and conversion reduces the precision.";
        CoCoLog.error(ERROR_CODE, msg, r.get_SourcePositionStart());
      }

    }

  }

}
