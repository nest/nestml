/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.resolving.CommonResolvingFilter;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

/**
 * All types in NESTML are predefined. This filter matches the type by name and returns if one exists
 *
 * @author plotnikov
 */
public class PredefinedTypesFilter extends CommonResolvingFilter<TypeSymbol> {
  public PredefinedTypesFilter() {
    super(TypeSymbol.KIND);
  }


  public Optional<Symbol> filter(ResolvingInfo resolvingInfo, String name, Map<String, Collection<Symbol>> symbols) {
    final Optional<TypeSymbol> typeSymbol = PredefinedTypes.getTypeIfExists(name);
    if (typeSymbol.isPresent()) {
      return Optional.of(typeSymbol.get());
    }
    else {
      return Optional.empty();
    }
  }

}
