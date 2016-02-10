/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.resolving.ResolvedSeveralEntriesException;
import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._symboltable.MethodSignaturePredicate;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

import static com.google.common.collect.Lists.newArrayList;

/**
 * Provides convenience methods
 *
 * @author plotnikov
 */
public class NESTMLSymbols {

  public static Optional<MethodSymbol> resolveMethod(
      final Scope scope,
      final String methodName,
      final List<String> parameters) {
    // it is OK. The cast is secured through the symboltable infrastructure
    @SuppressWarnings("unchecked")
    final Optional<MethodSymbol> standAloneFunction = (Optional<MethodSymbol>)
        scope.resolve(new MethodSignaturePredicate(methodName, parameters));

    final String calleeVariableNameCandidate = Names.getQualifier(methodName);
    final String simpleMethodName = Names.getSimpleName(methodName);

    if (!calleeVariableNameCandidate.isEmpty()) {
      final Optional<VariableSymbol> calleeVariableSymbol
          = scope.resolve(calleeVariableNameCandidate, VariableSymbol.KIND);
      if (calleeVariableSymbol.isPresent()) {

        final Optional<MethodSymbol> builtInMethod
            = calleeVariableSymbol.get().getType().getBuiltInMethod(simpleMethodName); // TODO parameters are not considered!
        if (standAloneFunction.isPresent() && builtInMethod.isPresent()) {
          final String errorDescription = "Unambiguous function exception. Function '"
              + simpleMethodName + "'. Can be resolved as a standalone function and as a method of: '"
              + calleeVariableSymbol + "' variable.";

          throw new RuntimeException(errorDescription);
        }

        if (builtInMethod.isPresent()) {
          return builtInMethod;
        }

      }

    }

    return standAloneFunction;
  }

  public static Optional<VariableSymbol> resolve(final String variableName, final Scope scope) {
    try {
      return scope.resolve(variableName, VariableSymbol.KIND);
    }
    catch (ResolvedSeveralEntriesException e) {
      Log.warn("The variable '" + variableName + "' is defined multiple times.");
    }
    return Optional.empty();
  }

  public static boolean isSetterPresent(
      final String aliasVar,
      final String varTypeName,
      final Scope scope) {
    final String setterName = "set_" + aliasVar;
    final Optional<MethodSymbol> setter = NESTMLSymbols.resolveMethod(
        scope,
        setterName,
        newArrayList(varTypeName));

    if (!setter.isPresent()) {
      return false;
    }
    else {
      final TypeSymbol setterType = setter.get().getParameterTypes().get(0);

      return setterType.getName().endsWith(varTypeName);
    }

  }

}
