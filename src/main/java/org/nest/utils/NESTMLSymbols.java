/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._symboltable.NESTMLMethodSignaturePredicate;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.List;
import java.util.Optional;

/**
 * Provides convenience methods
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 * @since 0.0.1
 */
public class NESTMLSymbols {

  public static Optional<MethodSymbol> resolveMethod(
      final Scope scope,
      final String methodName,
      final List<String> parameters) {
    // it is OK. The cast is secured through the symboltable infrastructure
    @SuppressWarnings("unchecked")
    final Optional<MethodSymbol> standAloneFunction = (Optional<MethodSymbol>)
        scope.resolve(new NESTMLMethodSignaturePredicate(methodName, parameters));

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

}
