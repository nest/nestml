/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.utils.NESTMLSymbols.resolveMethod;

/**
 * Checks that methods are defined and used with correct types.
 *
 * @author ippen, plotnikov
 */
public class FunctionDoesNotExist implements CommonsASTFunctionCallCoCo {
  public static final String ERROR_CODE = "SPL_FUNCTION_DOES_NOT_EXIST";
  private static final String ERROR_MSG_FORMAT = "The function '%s' is not defined";

  @Override
  public void check(final ASTFunctionCall astFunctionCall) {
    checkArgument(astFunctionCall.getEnclosingScope().isPresent(), "No scope assigned. run symboltable creator.");
    final Scope scope = astFunctionCall.getEnclosingScope().get();

    final String methodName = astFunctionCall.getCalleeName();

    final ExpressionTypeCalculator expressionTypeCalculator =  new ExpressionTypeCalculator();

    final List<String> argTypeNames = Lists.newArrayList();

    for (int i = 0; i < astFunctionCall.getArgs().size(); ++i) {
      final ASTExpr arg = astFunctionCall.getArgs().get(i);
      final Either<TypeSymbol, String> argType = expressionTypeCalculator.computeType(arg);
      if (argType.isValue()) {
        argTypeNames.add(argType.getValue().getName());
      }
      else {
        Log.warn(ERROR_CODE + ": Cannot compute the type: " + arg);
        return;
      }

    }

    final Optional<MethodSymbol> method = resolveMethod(methodName, argTypeNames, scope);

    if (!method.isPresent()) {
      Log.error(
          ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, methodName)
              + " with the signature '" + Joiner.on(",").join(argTypeNames) + "'",
          astFunctionCall.get_SourcePositionStart());
    }

  }

}
