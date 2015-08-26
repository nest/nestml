/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols.references;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.references.CommonSymbolReference;
import de.monticore.symboltable.references.SymbolReference;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;

/**
 * Represents a reference to a nestml type.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLNeuronSymbolReference extends NESTMLNeuronSymbol implements SymbolReference<NESTMLNeuronSymbol> {

  private final SymbolReference<NESTMLNeuronSymbol> typeReference;

  public NESTMLNeuronSymbolReference(final String name, NESTMLNeuronSymbol.Type type, Scope definingScopeOfReference) {
    super(name, type);
    typeReference = new CommonSymbolReference<>(name, NESTMLNeuronSymbol.KIND, definingScopeOfReference);
  }

  @Override
  public NESTMLNeuronSymbol getReferencedSymbol() {
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
