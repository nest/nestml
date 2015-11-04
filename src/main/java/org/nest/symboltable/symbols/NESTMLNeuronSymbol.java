/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.symbols;

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import de.monticore.symboltable.CommonScopeSpanningSymbol;
import de.monticore.symboltable.Symbol;
import org.nest.nestml._symboltable.NESTMLMethodSignaturePredicate;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.nest.symboltable.symbols.NESTMLVariableSymbol.BlockType.INPUT_BUFFER_CURRENT;

/**
 * Represents the entire neuron, e.g. iaf_neuron.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLNeuronSymbol extends CommonScopeSpanningSymbol {

  public final static NESTMLNeuronSymbolKind KIND = new NESTMLNeuronSymbolKind();

  private final Type type;

  public NESTMLNeuronSymbol(final String name, final Type type) {
    super(name, KIND);
    this.type = type;
  }

  public Type getType() {
    return type;
  }

  @Override
  public String toString() {
    return "NESTMLNeuronSymbol(" + getFullName() + "," + type + ")";
  }

  public Optional<NESTMLVariableSymbol> getVariableByName(String variableName) {
    return spannedScope.resolveLocally(variableName, NESTMLVariableSymbol.KIND);
  }

  public Optional<NESTMLMethodSymbol> getMethodByName(String methodName) {
    return getMethodByName(methodName, Lists.newArrayList());
  }

  public List<NESTMLVariableSymbol> getCurrentBuffers() {
    final Collection<NESTMLVariableSymbol> variableSymbols
        = spannedScope.resolveLocally(NESTMLVariableSymbol.KIND);
    return variableSymbols.stream()
        .filter(variable -> variable.getBlockType().equals(INPUT_BUFFER_CURRENT))
        .collect(Collectors.toList());
  }

  @SuppressWarnings("unchecked") // Resolving filter does the type checking
  public Optional<NESTMLMethodSymbol> getMethodByName(String methodName, List<String> parameters) {
    final Optional<? extends Symbol> result
        = spannedScope.resolve(new NESTMLMethodSignaturePredicate(methodName, parameters));
    if (result.isPresent()) {
      Preconditions.checkState(result.get() instanceof NESTMLMethodSymbol);
    }

    return (Optional<NESTMLMethodSymbol>) result;
  }

  public enum Type { NEURON, COMPONENT }
}
