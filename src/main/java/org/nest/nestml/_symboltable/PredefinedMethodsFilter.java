/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.predefined.PredefinedFunctions;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.MethodSymbol;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * TODO
 *
 * @author plotnikov
 */
public class PredefinedMethodsFilter extends CommonResolvingFilter<MethodSymbol> {

  public PredefinedMethodsFilter(
      final Class<MethodSymbol> symbolClass,
      final SymbolKind targetKind) {
    super(symbolClass, targetKind);
  }

  @Override
  public Optional<MethodSymbol> filter(
      final ResolvingInfo resolvingInfo,
      final String name,
      final List<Symbol> symbols) {
    final Optional<MethodSymbol> foundPredefinedMethod = PredefinedFunctions.getMethodSymbol(name);

    if (foundPredefinedMethod.isPresent()) {

      if (!symbols.contains(foundPredefinedMethod.get())) {
        symbols.add(foundPredefinedMethod.get());
      }
      else {
        System.out.println();
      }

      symbols.add(foundPredefinedMethod.get());
    }

    return  foundPredefinedMethod;
  }

}
