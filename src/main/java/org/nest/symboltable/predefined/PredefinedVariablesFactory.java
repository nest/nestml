/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.predefined;

import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Maps;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

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
  private static final String E_CONSTANT = "E";
  private static final NESTMLNeuronSymbol predefinedComponent = new NESTMLNeuronSymbol("Math",
      NESTMLNeuronSymbol.Type.COMPONENT);

  private final Map<String, NESTMLVariableSymbol> name2VariableSymbol = Maps.newHashMap();

  public PredefinedVariablesFactory(PredefinedTypesFactory predefinedTypesFactory) {
    registerVariable(E_CONSTANT, predefinedTypesFactory.getType("real"));

  }

  private void registerVariable(
      final String variableName, final NESTMLTypeSymbol type) {
    final NESTMLVariableSymbol variableSymbol = new NESTMLVariableSymbol(variableName);
    variableSymbol.setDeclaringType(predefinedComponent);
    variableSymbol.setType(type);
    name2VariableSymbol.put(variableName, variableSymbol);
  }

  public Set<NESTMLVariableSymbol> gerVariables() {
    return ImmutableSet.copyOf(name2VariableSymbol.values());
  }

}
