/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import de.monticore.symboltable.CommonScope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;
import org.nest.symboltable.symbols.NeuronSymbol;

import java.util.Optional;

/**
 * Provides the possibility resolve symbols from the inherited symbols
 *
 * @author plotnikov
 */
public class NeuronScope extends CommonScope {
  @Override
  public <T extends Symbol> Optional<T> resolve(String symbolName, SymbolKind kind) {
    // TODO PN rather resolveLocally, then in the super types, and finally in enclosing scope
    Optional<T> resolvedSymbol = super.resolve(symbolName, kind);


    if (!resolvedSymbol.isPresent()) {
      final NeuronSymbol neuronSymbol = ((Optional<NeuronSymbol>) getSpanningSymbol()).get();
      if (neuronSymbol.getBaseNeuron().isPresent()) {
        resolvedSymbol = neuronSymbol.getBaseNeuron().get().getSpannedScope()
            .resolveDown(symbolName, kind);
        if (!resolvedSymbol.isPresent()) {
          System.out.printf("");
        }
      }

    }

    return resolvedSymbol;
  }

  private <T extends Symbol> Optional<T> resolveInSupearTypes(String symbolName, SymbolKind kind) {
    return null;
  }

}
