/*
 * FunctionDoesNotExist.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.nest.nestml._cocos;

import com.google.common.base.Joiner;
import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._ast.ASTFunctionCall;
import org.nest.nestml._symboltable.symbols.MethodSymbol;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.utils.AstUtils;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkArgument;
import static org.nest.nestml._symboltable.NestmlSymbols.resolveMethod;

/**
 * Checks that methods are defined and used with correct types.
 *
 * @author ippen, plotnikov
 */
public class FunctionDoesNotExist implements NESTMLASTFunctionCallCoCo {

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
