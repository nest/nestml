/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols.references;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.references.CommonSymbolReference;
import de.monticore.symboltable.references.SymbolReference;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;

/**
 * Represents a reference to a nestml type.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLTypeSymbolReference extends NESTMLTypeSymbol implements
    SymbolReference<NESTMLTypeSymbol> {

  private final SymbolReference<NESTMLTypeSymbol> typeReference;

  public NESTMLTypeSymbolReference(final String name, Type type, Scope definingScopeOfReference) {
    super(name, type);
    typeReference = new CommonSymbolReference<>(name, NESTMLTypeSymbol.KIND, definingScopeOfReference);
  }

  @Override
  public NESTMLTypeSymbol getReferencedSymbol() {
    return typeReference.getReferencedSymbol();
  }

  @Override
  public boolean existsReferencedSymbol() {
    return typeReference.existsReferencedSymbol();
  }

  @Override public boolean isReferencedSymbolLoaded() {
    return typeReference.isReferencedSymbolLoaded();
  }

  @Override
  public String getName() {
    return typeReference.getReferencedSymbol().getName();
  }

  @Override
  public Type getType() {
    return typeReference.getReferencedSymbol().getType();
  }


}
