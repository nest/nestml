/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolPredicate;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;

import java.util.ArrayList;
import java.util.List;

import static com.google.common.base.Strings.emptyToNull;
import static java.util.Objects.requireNonNull;

public class NESTMLMethodSignaturePredicate implements SymbolPredicate {

  private final String expectedMethodName;
  private final List<String> expectedParameterTypes = new ArrayList<>();

  public NESTMLMethodSignaturePredicate(final String methodName,
                                        final List<String> parameters) {
    this.expectedMethodName = requireNonNull(emptyToNull(methodName));

    expectedParameterTypes.addAll(parameters);

  }

  @Override
  public boolean apply(final Symbol symbol) {
    if ((symbol != null) &&
        symbol.isKindOf(NESTMLMethodSymbol.KIND) &&
        (symbol instanceof NESTMLMethodSymbol)) {
      final NESTMLMethodSymbol methodSymbol = (NESTMLMethodSymbol) symbol;

      if (methodSymbol.getName().equals(expectedMethodName) &&
          (methodSymbol.getParameterTypes().size() == expectedParameterTypes.size())) {
        for (int i=0; i < methodSymbol.getParameterTypes().size(); i++) {
          final String expectedType = expectedParameterTypes.get(i);
          final String actualType = methodSymbol.getParameterTypes().get(i).getFullName();

          if (!actualType.equals(expectedType)) {
            return false;
          }
        }

        return true;
      }

    }

    return false;
  }

}
