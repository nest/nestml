/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._cocos.NESTMLASTFunctionCoCo;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.base.Preconditions.checkState;
import static de.se_rwth.commons.logging.Log.error;
import static org.nest.utils.NESTMLSymbols.resolveMethod;

/**
 * Prohibits definition of setter/getters for declared variables which are not aliases.
 *
 * @author (last commit) ippen, plotnikov
 * @since 0.0.1
 */
public class NESTGetterSetterFunctionNames implements NESTMLASTFunctionCoCo {

  public static final String ERROR_CODE = "NESTML_GETTER_SETTER_FUNCTION_NAMES";

  public void check(final ASTFunction fun) {
    String funName = fun.getName();

    final Optional<? extends Scope> enclosingScope = fun.getEnclosingScope();
    checkState(enclosingScope.isPresent(),
        "There is no scope assigned to the AST node: " + fun.getName());

    NESTMLMethodSymbol methodSymbol = getMethodEntry(fun, enclosingScope.get());

    if (methodSymbol.getDeclaringNeuron().getType() == NESTMLNeuronSymbol.Type.COMPONENT
        && funName.equals("get_instance")
        && methodSymbol.getParameterTypes().size() == 0) {

      final String msg = "The function '"
          + funName
          + "' is going to be generated. Please use another name.";
      error(ERROR_CODE + ":" + msg, fun.get_SourcePositionStart());
      return;
    }

    if (funName.startsWith("get_") || funName.startsWith("set_")) {
      String varName = funName.substring(4);

      Optional<NESTMLVariableSymbol> var = enclosingScope.get()
          .resolve(varName, NESTMLVariableSymbol.KIND);

      if (var.isPresent()) {

        if (funName.startsWith("set_") &&
            methodSymbol.getParameterTypes().size() == 1 && !var.get().isAlias()) {
          final String msg = "The function '" + funName + "' is going to be generated, since"
              + " there is a variable called '" + varName + "'.";
          error(ERROR_CODE + ":" + msg, fun.get_SourcePositionStart());
        }

        if (funName.startsWith("get_")
            && methodSymbol.getParameterTypes().size() == 0) {
          final String msg = "The function '" + funName + "' is going to be generated, since"
              + " there is a variable called '" + varName + "'.";
          error(ERROR_CODE + ":" + msg, fun.get_SourcePositionStart());
        }

      }

    }

  }

  private NESTMLMethodSymbol getMethodEntry(final ASTFunction fun, final Scope scope) {
    final Optional<NESTMLMethodSymbol> methodSymbol;

    if (!fun.getParameters().isPresent()) {
      methodSymbol = resolveMethod(scope, fun.getName(), Lists.newArrayList());
    }
    else {
      List<String> parameters = Lists.newArrayList();
      for (int i = 0; i < fun.getParameters().get().getParameters().size(); ++i) {
        String parameterTypeFqn = Names.getQualifiedName(
            fun.getParameters().get().getParameters().get(i).getType().getParts());
        parameters.add(parameterTypeFqn);
      }

      methodSymbol = resolveMethod(scope, fun.getName(), parameters);
    }

    checkState(methodSymbol.isPresent(), "Cannot resolve the method: " + fun.getName());
    return methodSymbol.get();
  }

}
