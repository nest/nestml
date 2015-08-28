/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.cocos;

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import static de.se_rwth.commons.logging.Log.error;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.ASTFunctionCall;
import org.nest.spl._cocos.SPLASTFunctionCallCoCo;
import org.nest.spl.symboltable.typechecking.ExpressionTypeCalculator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Checks that methods are defined and used with correct types.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class FunctionDoesntExist implements SPLASTFunctionCallCoCo {
  public static final String ERROR_CODE = "SPL_FUNCTION_DOESNT_EXIST";
  private static final String ERROR_MSG_FORMAT = "The function '%s' is not defined";
  private final PredefinedTypesFactory predefinedTypesFactory;

  public FunctionDoesntExist(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  @Override
  public void check(final ASTFunctionCall funcall) {
    checkArgument(funcall.getEnclosingScope().isPresent(), "No scope assigned. run symboltable creator.");
    final Scope scope = funcall.getEnclosingScope().get();

    final String methodName = Names.getQualifiedName(funcall.getQualifiedName().getParts());

    final ExpressionTypeCalculator expressionTypeCalculator =  new ExpressionTypeCalculator(
        predefinedTypesFactory);

    final List<String> argTypeNames = Lists.newArrayList();

    for (int i = 0; i < funcall.getArgList().getArgs().size(); ++i) {
      final ASTExpr arg = funcall.getArgList().getArgs().get(i);
      final NESTMLTypeSymbol argType = expressionTypeCalculator.computeType(arg);
      argTypeNames.add(argType.getName());
    }

    final Optional<NESTMLMethodSymbol> method
        = NESTMLSymbols.resolveMethod(scope, methodName, argTypeNames);

    if (!method.isPresent()) {
      Log.error(
          ERROR_CODE + ":" + String.format(ERROR_MSG_FORMAT, methodName)
              + " with the signature '" + Joiner.on(",").join(argTypeNames) + "'",
          funcall.get_SourcePositionStart());
    }

  }

}
