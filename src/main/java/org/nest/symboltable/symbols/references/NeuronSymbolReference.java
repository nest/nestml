/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols.references;

import de.monticore.symboltable.Scope;
import de.monticore.symboltable.references.CommonSymbolReference;
import de.monticore.symboltable.references.SymbolReference;
import org.nest.symboltable.symbols.NeuronSymbol;

/**
 * Represents a reference to a nestml neuron.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NeuronSymbolReference extends NeuronSymbol implements SymbolReference<NeuronSymbol> {

  private final SymbolReference<NeuronSymbol> typeReference;

  public NeuronSymbolReference(final String name, NeuronSymbol.Type type, Scope definingScopeOfReference) {
    super(name, type);
    typeReference = new CommonSymbolReference<>(name, NeuronSymbol.KIND, definingScopeOfReference);
  }

  @Override
  public NeuronSymbol getReferencedSymbol() {
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
