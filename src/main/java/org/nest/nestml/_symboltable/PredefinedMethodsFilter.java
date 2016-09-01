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
import org.nest.symboltable.symbols.MethodSymbol;

import java.util.List;
import java.util.Optional;

import static org.nest.symboltable.predefined.PredefinedFunctions.getMethodSymbolIfExists;

/**
 * TODO
 *
 * @author plotnikov
 */
public class PredefinedMethodsFilter extends CommonResolvingFilter<MethodSymbol> {

  public PredefinedMethodsFilter(
      final SymbolKind targetKind) {
    super(targetKind);


  }

  @Override
  public Optional<Symbol> filter(ResolvingInfo resolvingInfo, String name,
      List<Symbol> symbols) {
    final Optional<MethodSymbol> foundPredefinedMethod = getMethodSymbolIfExists(name);

    if (foundPredefinedMethod.isPresent()) {

      return Optional.of(foundPredefinedMethod.get());
    }

    return Optional.empty();
  }


}
