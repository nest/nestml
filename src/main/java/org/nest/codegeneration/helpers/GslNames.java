package org.nest.codegeneration.helpers;

import org.nest.nestml._symboltable.symbols.VariableSymbol;

/**
 * The class is responsible code snippets that access variables, e.g. locally, from state or parameters.
 * TODO: this class can be parametrized to support GSL style instantiation
 * @author plotnikov
 */
public class GslNames {

  public static String arrayIndex(final VariableSymbol variableSymbol) {
      return "State_::" + Names.convertToCPPName(variableSymbol.getName()) ;
  }

  public static String name(final VariableSymbol variableSymbol) {
    if (variableSymbol.definedByODE()) {
      return "y[State_::" + Names.convertToCPPName(variableSymbol.getName()) + "]";
    }
    else {
      return Names.name(variableSymbol);
    }

  }

  public static String getter(final VariableSymbol variableSymbol) {
    return Names.getter(variableSymbol);
  }


  public static String setter(final VariableSymbol variableSymbol) {
    return Names.setter(variableSymbol);
  }

  public static String bufferValue(final VariableSymbol buffer) {
    return Names.bufferValue(buffer);
  }

  public static String convertToCPPName(final String variableName) {
    return Names.convertToCPPName(variableName);
  }

}
