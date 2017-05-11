
/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTFunction;
import org.nest.symboltable.NestmlSymbols;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;

/**
 * Prohibits definition of setter/getters for declared variables which are not aliases.
 *
 * @author (last commit) ippen, plotnikov
 */
public class GetterSetterFunctionNames implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_GETTER_SETTER_FUNCTION_NAMES";
  NestmlErrorStrings errorStrings = NestmlErrorStrings.getInstance();

  public void check(final ASTFunction fun) {
    String funName = fun.getName();

    final Optional<? extends Scope> enclosingScope = fun.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node: " + fun.getName());

    Optional<MethodSymbol> methodSymbol = NestmlSymbols.resolveMethod(fun);

    if (methodSymbol.isPresent()) {
      if (methodSymbol.get().getDeclaringNeuron().getType() == NeuronSymbol.Type.COMPONENT
          && funName.equals("get_instance")
          && methodSymbol.get().getParameterTypes().size() == 0) {

        final String msg = errorStrings.getErrorMsgGet_InstanceDefined(this);

        error(msg, fun.get_SourcePositionStart());
        return;
      }

      if (funName.startsWith("get_") || funName.startsWith("set_")) {
        String varName = funName.substring(4);

        final Optional<VariableSymbol> var = enclosingScope.get().resolve(varName, VariableSymbol.KIND);

        if (var.isPresent()) {
          if (funName.startsWith("set_")) {
            final String msg = errorStrings.getErrorMsgGeneratedFunctionDefined(this,funName,varName);

            error(msg, fun.get_SourcePositionStart());
          }

          if (funName.startsWith("get_")) {
            final String msg = errorStrings.getErrorMsgGeneratedFunctionDefined(this,funName,varName);

            error(msg, fun.get_SourcePositionStart());
          }

        }
        else {
          Log.warn(ERROR_CODE + ":" + "Cannot resolve the variable: " + varName);
        }

      }

    }
    else {
      Log.warn("The function is" + funName + " undefined.");
    }

  }

}
