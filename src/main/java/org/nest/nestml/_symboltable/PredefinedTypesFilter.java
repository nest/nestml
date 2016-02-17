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
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since TODO
 */
public class PredefinedTypesFilter extends CommonResolvingFilter<TypeSymbol> {
  public PredefinedTypesFilter(
      final Class<TypeSymbol> symbolClass,
      final SymbolKind targetKind) {
    super(symbolClass, targetKind);
  }

  @Override
  public Optional<TypeSymbol> filter(
      final ResolvingInfo resolvingInfo,
      final String name,
      final List<Symbol> symbols) {

    return PredefinedTypes.getPredefinedTypeIfExists(name);
  }

}
