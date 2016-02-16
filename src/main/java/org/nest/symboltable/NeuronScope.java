/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import de.monticore.symboltable.CommonScope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;

import java.util.Optional;

/**
 * TODO
 *
 * @author plotnikov
 */
public class NeuronScope extends CommonScope {
  @Override
  public <T extends Symbol> Optional<T> resolve(String symbolName, SymbolKind kind) {
    // TODO PN rather resolveLocally, then in the super types, and finally in enclosing scope
    Optional<T> resolvedSymbol = super.resolve(symbolName, kind);


    /*if (!resolvedSymbol.isPresent()) {
      // To resolve symbols of super types, they must at least be protected.
      resolvedSymbol = resolveInSuperTypes(symbolName, kind);
    }*/

    return resolvedSymbol;
  }

  private <T extends Symbol> Optional<T> resolveInSuperTypes(String symbolName, SymbolKind kind) {
    return null;
  }

}
