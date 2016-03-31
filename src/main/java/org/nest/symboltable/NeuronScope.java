/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable;

import com.google.common.collect.Sets;
import de.monticore.symboltable.CommonScope;
import de.monticore.symboltable.Symbol;
import de.monticore.symboltable.SymbolKind;
import de.monticore.symboltable.modifiers.AccessModifier;
import de.monticore.symboltable.resolving.ResolvingInfo;
import org.nest.symboltable.symbols.NeuronSymbol;

import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;

/**
 * Provides the possibility resolve symbols from the inherited symbols
 *
 * @author plotnikov
 */
public class NeuronScope extends CommonScope {

  @Override protected <T extends Symbol> Set<T> resolveManyLocally(
      final ResolvingInfo resolvingInfo,
      final String name,
      final SymbolKind kind,
      final AccessModifier modifier, Predicate<Symbol> predicate) {
    Set<T> symbols = super.resolveManyLocally(resolvingInfo, name, kind, modifier, predicate);
    if (!symbols.isEmpty()) {
      return symbols;
    }

    final NeuronSymbol neuronSymbol = ((Optional<NeuronSymbol>) getSpanningSymbol()).get();
    if (neuronSymbol.getBaseNeuron().isPresent()) {
      final Set<Symbol> result = Sets.newHashSet();
      Optional<Symbol> resolvedSymbol = neuronSymbol.getBaseNeuron().get().getSpannedScope()
          .resolveLocally(kind).stream().filter(symbol -> symbol.getName().equals(name)).findFirst();
      resolvedSymbol.ifPresent(result::add);
      return (Set<T>) result;
    }
    else {
      return symbols;
    }
  }


  @Override public boolean exportsSymbols() {
    return true;
  }
}
