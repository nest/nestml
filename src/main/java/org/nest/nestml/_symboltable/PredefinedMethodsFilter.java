/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.symbols.MethodSymbol;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

import static org.nest.symboltable.predefined.PredefinedFunctions.getMethodSymbolIfExists;

/**
 * Returns a predefined methods if one exists: e.g. pow, exp, ...
 *
 * @author plotnikov
 */
public class PredefinedMethodsFilter extends CommonResolvingFilter<MethodSymbol> {

  public PredefinedMethodsFilter() {
    super(MethodSymbol.KIND);


  }

  public Optional<Symbol> filter(ResolvingInfo resolvingInfo, String name, Map<String, Collection<Symbol>> symbols) {

    final Optional<MethodSymbol> foundPredefinedMethod = getMethodSymbolIfExists(name);

    if (foundPredefinedMethod.isPresent()) {

      return Optional.of(foundPredefinedMethod.get());
    }

    return Optional.empty();
  }


}
