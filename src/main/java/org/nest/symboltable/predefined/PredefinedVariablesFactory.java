/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Maps;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.util.Map;
import java.util.Set;

/**
 * Defines a set with implicit type functions, like {@code print, pow, ...}
 *
 * @author plotnikov
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class PredefinedVariablesFactory {
  private static final String E_CONSTANT = "e";
  private static final NeuronSymbol predefinedComponent = new NeuronSymbol("Math",
      NeuronSymbol.Type.COMPONENT);

  private final Map<String, VariableSymbol> name2VariableSymbol = Maps.newHashMap();

  public PredefinedVariablesFactory() {
    registerVariable(E_CONSTANT, PredefinedTypes.getRealType());

  }

  private void registerVariable(
      final String variableName, final TypeSymbol type) {
    final VariableSymbol variableSymbol = new VariableSymbol(variableName);
    variableSymbol.setDeclaringType(predefinedComponent);
    variableSymbol.setType(type);
    name2VariableSymbol.put(variableName, variableSymbol);
  }

  public Set<VariableSymbol> gerVariables() {
    return ImmutableSet.copyOf(name2VariableSymbol.values());
  }

}
