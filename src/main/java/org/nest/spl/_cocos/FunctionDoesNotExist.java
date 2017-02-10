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
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.symboltable.NestmlSymbols.resolveMethod;

/**
 * Checks that methods are defined and used with correct types.
 *
 * @author ippen, plotnikov
 */
public class FunctionDoesNotExist implements CommonsASTFunctionCallCoCo {

  @Override
  public void check(final ASTFunctionCall astFunctionCall) {
    checkArgument(astFunctionCall.getEnclosingScope().isPresent(), "No scope assigned. run symboltable creator.");
    final Scope scope = astFunctionCall.getEnclosingScope().get();

    final String methodName = astFunctionCall.getCalleeName();


    final List<String> argTypeNames = Lists.newArrayList();
    final List<String> prettyArgTypeNames = Lists.newArrayList();

    for (ASTExpr arg :  astFunctionCall.getArgs()) {
      final Either<TypeSymbol, String> argType = arg.getType();
      if (argType.isValue()) {
        prettyArgTypeNames.add(argType.getValue().prettyPrint());
        argTypeNames.add(argType.getValue().getName());
      }
      else {
        Log.warn(SplErrorStrings.code(this) + ": Cannot compute the type: " + AstUtils.toString(arg) + " : ", arg.get_SourcePositionStart());
        return;
      }

    }

    final Optional<MethodSymbol> method = resolveMethod(methodName, argTypeNames, scope);

    if (!method.isPresent()) {
      Log.error(SplErrorStrings.message(this, methodName, Joiner.on(",").join(prettyArgTypeNames)),
                astFunctionCall.get_SourcePositionStart());
    }

  }

}
