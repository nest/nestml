/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import com.google.common.collect.Lists;
import de.monticore.symboltable.CommonScope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.symbols.NeuronSymbol;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Provides the possibility resolve symbols from the inherited symbols
 *
 * @author plotnikov
 */
public class NeuronScope extends CommonScope {

  /**
   * TODO: big hack! review it with PN.
   * @param resolvingInfo
   * @param name
   * @param kind
   * @param <T>
   * @return
   */
  @Override
  protected <T extends Symbol> Collection<T> resolveManyLocally(
      ResolvingInfo resolvingInfo, String name, SymbolKind kind) {
    Collection<T> symbols = super.resolveManyLocally(resolvingInfo, name, kind);
    if (!symbols.isEmpty()) {
      return symbols;
    }

    final NeuronSymbol neuronSymbol = ((Optional<NeuronSymbol>) getSpanningSymbol()).get();
    if (neuronSymbol.getBaseNeuron().isPresent()) {
      final List<Symbol> result = Lists.newArrayList();
      Optional<Symbol> resolvedSymbol = neuronSymbol.getBaseNeuron().get().getSpannedScope()
          .resolveLocally(kind).stream().filter(symbol -> symbol.getName().equals(name)).findFirst();
      resolvedSymbol.ifPresent(result::add);
      return (Collection<T>) result;
    }
    else {
      return symbols;
    }
  }

  @Override
  public <T extends Symbol> Optional<T> resolve(String symbolName, SymbolKind kind) {
    // TODO PN rather resolveLocally, then in the super types, and finally in enclosing scope
    Optional<T> resolvedSymbol = super.resolve(symbolName, kind);


    if (!resolvedSymbol.isPresent()) {


    }

    return resolvedSymbol;
  }

  @Override public boolean exportsSymbols() {
    return true;
  }
}
