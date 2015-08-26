/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.utils;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._symboltable.NESTMLMethodSignaturePredicate;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

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

  public static Optional<NESTMLMethodSymbol> resolveMethod(
      final Scope scope,
      final String methodName,
      final List<String> parameters) {
    // it is OK. The cast is secured through the symboltable infrastructure
    @SuppressWarnings("unchecked")
    final Optional<NESTMLMethodSymbol> standAloneFunction = (Optional<NESTMLMethodSymbol>)
        scope.resolve(new NESTMLMethodSignaturePredicate(methodName, parameters));

    final String calleeVariableNameCandidate = Names.getQualifier(methodName);
    final String simpleMethodName = Names.getSimpleName(methodName);

    if (!calleeVariableNameCandidate.isEmpty()) {
      final Optional<NESTMLVariableSymbol> calleeVariableSymbol
          = scope.resolve(calleeVariableNameCandidate, NESTMLVariableSymbol.KIND);
      if (calleeVariableSymbol.isPresent()) {

        final Optional<NESTMLMethodSymbol> builtInMethod
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
