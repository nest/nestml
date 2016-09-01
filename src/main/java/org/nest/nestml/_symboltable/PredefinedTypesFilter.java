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
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.List;
import java.util.Optional;

/**
 * TODO
 *
 * @author plotnikov
 */
public class PredefinedTypesFilter extends CommonResolvingFilter<TypeSymbol> {
  public PredefinedTypesFilter(
      final SymbolKind targetKind) {
    super(targetKind);
  }

  @Override
  public Optional<Symbol> filter(
      final ResolvingInfo resolvingInfo,
      final String name,
      final List<Symbol> symbols) {
    final Optional<TypeSymbol> typeSymbol = PredefinedTypes.getTypeIfExists(name);
    if (typeSymbol.isPresent()) {
      return Optional.of(typeSymbol.get());
    }
    else {
      return Optional.empty();
    }

  }

}
