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
import org.nest.units.unitrepresentation.SIData;

import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Defines a set with implicit variables and constants, like {@code e, t, ...}
 *
 * @author plotnikov
 */
public class PredefinedVariables {
  public static final String E_CONSTANT = "e";
  public static final String TIME_CONSTANT = "t";
  private static final NeuronSymbol predefinedComponent =
      new NeuronSymbol("Math", NeuronSymbol.Type.COMPONENT);

  private static final Map<String, VariableSymbol> name2VariableSymbol = Maps.newHashMap();

  static  {
    registerVariable(E_CONSTANT, PredefinedTypes.getRealType());
    registerVariable(TIME_CONSTANT, PredefinedTypes.getMS());

    for(String unitName : SIData.getCorrectSIUnits()){
      TypeSymbol typeSymbol = PredefinedTypes.getType(unitName);
      registerVariable(unitName,typeSymbol);
    }
  }

  private static void registerVariable(
      final String variableName, final TypeSymbol type) {
    final VariableSymbol variableSymbol = new VariableSymbol(variableName);
    variableSymbol.setDeclaringType(predefinedComponent);
    variableSymbol.setType(type);
    variableSymbol.setPredefined(true);
    name2VariableSymbol.put(variableName, variableSymbol);
  }

  public static VariableSymbol getTimeConstant() {
    return name2VariableSymbol.get(TIME_CONSTANT);
  }

  public static Set<VariableSymbol> gerVariables() {
    return ImmutableSet.copyOf(name2VariableSymbol.values());
  }

  public static Optional<VariableSymbol> getVariableIfExists(final String variableName) {
    if (name2VariableSymbol.containsKey(variableName)) {
      return Optional.of(name2VariableSymbol.get(variableName));
    }
    else {
      return Optional.empty();
    }
  }

}
