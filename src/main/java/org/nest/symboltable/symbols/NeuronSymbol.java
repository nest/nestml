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
import de.monticore.symboltable.SymbolKind;
import org.nest.nestml._symboltable.MethodSignaturePredicate;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.nest.symboltable.symbols.VariableSymbol.BlockType.INPUT_BUFFER_CURRENT;
import static org.nest.symboltable.symbols.VariableSymbol.BlockType.INPUT_BUFFER_SPIKE;

/**
 * Represents the entire neuron, e.g. iaf_neuron.
 *
 * @author plotnikov
 */
public class NeuronSymbol extends CommonScopeSpanningSymbol {

  public final static NeuronSymbolKind KIND = new NeuronSymbolKind();

  private final Type type;

  public NeuronSymbol(final String name, final Type type) {
    super(name, KIND);
    this.type = type;
  }

  public Type getType() {
    return type;
  }

  @Override
  public String toString() {
    return "NeuronSymbol(" + getFullName() + "," + type + ")";
  }

  public Optional<VariableSymbol> getVariableByName(String variableName) {
    return spannedScope.resolveLocally(variableName, VariableSymbol.KIND);
  }

  public Optional<MethodSymbol> getMethodByName(String methodName) {
    return getMethodByName(methodName, Lists.newArrayList());
  }

  public List<VariableSymbol> getCurrentBuffers() {
    final Collection<VariableSymbol> variableSymbols
        = spannedScope.resolveLocally(VariableSymbol.KIND);
    return variableSymbols.stream()
        .filter(variable -> variable.getBlockType().equals(INPUT_BUFFER_CURRENT))
        .collect(Collectors.toList());
  }

  public List<VariableSymbol> getSpikeBuffers() {
    final Collection<VariableSymbol> variableSymbols
        = spannedScope.resolveLocally(VariableSymbol.KIND);
    return variableSymbols.stream()
        .filter(variable -> variable.getBlockType().equals(INPUT_BUFFER_SPIKE))
        .collect(Collectors.toList());
  }

  @SuppressWarnings("unchecked") // Resolving filter does the type checking
  public Optional<MethodSymbol> getMethodByName(String methodName, List<String> parameters) {
    final Optional<? extends Symbol> result
        = spannedScope.resolve(new MethodSignaturePredicate(methodName, parameters));
    if (result.isPresent()) {
      Preconditions.checkState(result.get() instanceof MethodSymbol);
    }

    return (Optional<MethodSymbol>) result;
  }

  public enum Type { NEURON, COMPONENT }

  public static class NeuronSymbolKind implements SymbolKind {

    protected NeuronSymbolKind() {
    }

  }

}
